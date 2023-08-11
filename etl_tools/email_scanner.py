# -*- coding: utf-8 -*-

from google_tools.google_api import pull_gsheet_data,write_single_cell_to_gsheet,df_to_gsheet_simple,get_alpha_column_from_df,clear_gsheet_tab
from google_tools.gmail_api import get_message_ids_from_key_word,get_df_from_msg_id,get_received_date_from_message_id
from etl_tools.looker_tools import download_looker_sql_runner,s3_looks_to_gsheet
from aws_tools.console_tools import push_local_file_to_s3, get_s3_file_list, push_df_to_s3
import datetime
import time
import os
import time
from etl_tools.email_custom_file_processing import sage_mec
import pytz
etl_workbook_id ="1QuxVh5cUxVf8OMStVcgzNxVyNv3LBad_6nrCKtN-j_E"
sheet_name = 'email_jobs'

def email_scanner(keyword=""):
    run_requests_df = pull_gsheet_data(etl_workbook_id,sheet_name)
    run_requests_df['orig_index'] = run_requests_df.index
    if keyword == "":
        email_requests_df = run_requests_df[(run_requests_df.run_now=='1')].reset_index(drop=True)
    else:
        email_requests_df = run_requests_df[(run_requests_df.key_word_in_subject == keyword)].reset_index(drop=True)
    
    eI = 0
    for er in email_requests_df['email_address']:
        try:
            er = email_requests_df['email_address'][eI]
            alpha_col = get_alpha_column_from_df(email_requests_df,'bot_message')
            edit_row = email_requests_df['orig_index'][eI]
            edit_address = alpha_col + str((edit_row+2))
            value = '...SotETL is working on it'
            write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)
            
            key_word_in_subject = email_requests_df['key_word_in_subject'][eI]
            filetype = email_requests_df['filetype'][eI]
            s3_bucket = email_requests_df['s3_bucket'][eI]
            s3_path = email_requests_df['s3_path'][eI]
            s3_file_name = email_requests_df['s3_file_name'][eI] + '.csv'
            storage_type = email_requests_df['storage_type'][eI]
            workbook_id = email_requests_df['gsheet_id'][eI]
            custom_processing_function = email_requests_df['custom_processing_function'][eI]
            gsheet_range = email_requests_df['publish_range'][eI]
            #get all msg ids for this key word
            msg_ids = get_message_ids_from_key_word(key_word_in_subject)
            today = datetime.date.today()

            if storage_type == 'raw_file archive':
                s3_file_list = get_s3_file_list(s3_bucket, s3_path)
                s3_file_list1 = []
                for file in s3_file_list:
                    s3_file = file['Key'].split("/")[-1]
                    if s3_file not in s3_file_list1 and (s3_file.find('xlsx') != -1 or s3_file.find('csv') != -1):
                        s3_file_list1.append(s3_file)

            mI = 0
            if storage_type == 'keep_latest_only':
                msg_ids = [msg_ids[0]]
            elif storage_type == 'latest_day_only':
                msg_ids = msg_ids[:20]
            for mid in msg_ids:
                try:
                    if storage_type == 'latest_day_only':
                        mid_date = get_received_date_from_message_id(mid)
                        print(str(mid) + " date = " + str(mid_date))
                        if mid_date == today:
                            file_name, df = get_df_from_msg_id(mid)
                        else:
                            file_name = 'do not publish'
                            df = []
                    else:
                        file_name, df = get_df_from_msg_id(mid)

                    if custom_processing_function == 'sage_mec':
                        df = sage_mec(df)
                    if len(df) > 0:
                        df['source_file'] = file_name
                        if mI == 0:
                            full_df = df
                            mI = 1
                        else:
                            full_df = full_df.append(df)

                    if storage_type == 'raw_file archive' and len(df) > 0:
                        df = df.replace(",", "", regex=True)
                        if filetype == 'csv' and file_name not in s3_file_list1:
                            df.to_csv(file_name, index=False)
                            push_local_file_to_s3(s3_bucket, s3_path, file_name, file_name)
                            print(file_name + " added to S3")
                        elif filetype == 'excel' and file_name not in s3_file_list1:
                            push_local_file_to_s3(s3_bucket, s3_path, file_name, file_name)
                            print(file_name + " added to S3")

                    os.remove(file_name)

                except:
                    print(str(mid) + " FAILED")

            tempfile_name = "tmp" + str(datetime.datetime.now())[:19].replace(":", "").replace(" ", "_")
            full_df = full_df.replace(",", "", regex=True)
            full_df.to_csv(tempfile_name, index=False)
            print(tempfile_name)
            # replace commas just in case
            if storage_type != 'raw_file archive':
                push_local_file_to_s3(s3_bucket, s3_path, s3_file_name, tempfile_name)
            os.remove(tempfile_name)

            #publish the file in a gsheet if desired
            if len(workbook_id) > 0:
                full_df['publish_time_utc'] = str(datetime.datetime.utcnow())
                if key_word_in_subject == 'Daily Vendor Prices - Current':
                    full_df = full_df[full_df.Pharmacy == 'PMH1']
                clear_gsheet_tab(workbook_id,gsheet_range)
                df_to_gsheet_simple(workbook_id,gsheet_range,full_df,delete_input=False)
                
            #write back to the sheet to indicate the run was complete
            alpha_col = get_alpha_column_from_df(email_requests_df,'last_updated')
            edit_row = email_requests_df['orig_index'][eI]
            edit_address = alpha_col + str((edit_row+2))
            tz = pytz.timezone('US/Pacific')
            value = str(datetime.datetime.now(tz))[:16]
            write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)
            #write a non error message
            alpha_col = get_alpha_column_from_df(email_requests_df,'bot_message')
            edit_row = email_requests_df['orig_index'][eI]
            edit_address = alpha_col + str((edit_row+2))
            value = '(none)'
            write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)

        except Exception as e:
             alpha_col = get_alpha_column_from_df(email_requests_df,'bot_message')
             edit_row = email_requests_df['orig_index'][eI]
             edit_address = alpha_col + str((edit_row+2))
             value = str(e)
             write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)
            
        eI = eI +1
    value = str(datetime.datetime.now())
    write_single_cell_to_gsheet(etl_workbook_id, 'latest_scans', 'B4', value)

def email_scan_run():
    try:
        email_scanner()
        print ("email checks complete " + str(datetime.datetime.now()))
    except Exception as e:
        print (str(e))
        print("email scan failed " + str(datetime.datetime.now()))


    
    
    
    