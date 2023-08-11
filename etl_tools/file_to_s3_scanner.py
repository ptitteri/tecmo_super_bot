# -*- coding: utf-8 -*-


from google_tools.google_api import pull_gsheet_data, write_df_to_gsheet,get_alpha_column_from_df,write_single_cell_to_gsheet,df_to_gsheet_simple
from aws_tools.console_tools import push_local_file_to_s3
import time
import pandas as pd
import numpy as np
import os
import datetime
import string
etl_workbook_id ="1QuxVh5cUxVf8OMStVcgzNxVyNv3LBad_6nrCKtN-j_E"
sheet_name = 'etl_jobs'

def file_to_s3_scanner():

    run_requests_df = pull_gsheet_data(etl_workbook_id,sheet_name)
    run_requests_df['orig_index'] = run_requests_df.index
    run_requests_df = run_requests_df[(run_requests_df['reference_link'] != "") & (run_requests_df['reference_link'].isnull()==False)]
    #local_folder = "C:\\Users\\peter.titterington\\Downloads\\"
    local_folder = "/Users/peteeti/Downloads/"

    #for each file that matches a run request id in the in run requests, pull the latest published file and push it to s3

    file_list = os.listdir(local_folder)

    run_requests_df['sql_id'] = run_requests_df.reference_link.str[-14:]

    for sql_id,rrdfI in zip(run_requests_df['sql_id'],run_requests_df['orig_index']):
        #print (sql_id)

        #pull all files with that id in the name
        publish_file = ""
        for f in file_list:
            if f.find(sql_id) != -1 and f.find('crdownload') == -1:
                try:
                    publish_file = f
                    print (publish_file)
                    s3_bucket = run_requests_df.s3_bucket[rrdfI]
                    s3_path = run_requests_df.s3_path[rrdfI]

                    publish_type = run_requests_df.type[rrdfI]
                    replace_flag = run_requests_df.replace_existing[rrdfI]
                    if replace_flag == 'add_timestamp':
                        file_stamp = str(datetime.datetime.now())[:19].replace(":","-").replace(" ","_") + "_bot_time"
                    else:
                        file_stamp = ""
                    s3_file_name = run_requests_df.file_name[rrdfI] + file_stamp +  ".csv"
                    #if the path doesn't exist, create it
                    push_local_file_to_s3(s3_bucket,s3_path,s3_file_name,local_folder + publish_file)
                    #check to see if I should just push right to a gsheet from here
                    #extra remove file commeand
                    try:
                        if publish_type == "simple_gsheet_import":
                            pub_df = pd.read_csv(local_folder + publish_file)
                            if len(pub_df) > 0:

                                pub_df['publish_time'] = str(datetime.datetime.now())[:16]
                                pub_sheet_id = run_requests_df.gsheet_id[rrdfI]
                                pub_tab = run_requests_df.gsheet_tab[rrdfI]
                                pop_range = run_requests_df.gsheet_range_to_populate[rrdfI]
                                # try:
                                #     row_start = int(pop_range[1:2])
                                # except:
                                #     row_start = int(pop_range[2:3])

                                header_range = pub_tab + "!" + pop_range

                                #body_range = header_range.replace(str(row_start),str(row_start+1))
                                df_to_gsheet_simple(pub_sheet_id,header_range,pub_df,delete_input=True)
                                #write_df_to_gsheet(pub_sheet_id,header_range,body_range,pub_df)
                    except Exception as e:
                        print(e)

                    try:
                        os.remove(local_folder + publish_file)
                    except:
                        print (publish_file + " already deleted")
                    #mark this file as run with a timestamp
                    ##find the last updated at column
                    alpha_col = get_alpha_column_from_df(run_requests_df,'last run at')
                    edit_address = alpha_col + str((rrdfI+2))
                    value = str(datetime.datetime.now())[:16]
                    write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)
                    #write non-error message
                    alpha_col = get_alpha_column_from_df(run_requests_df,'error_code')
                    edit_address = alpha_col + str((rrdfI+2))
                    value = "(none)"
                    write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)



                except Exception as e:
                    print ("file_scanner_failed")
                    alpha_col = get_alpha_column_from_df(run_requests_df,'error_code')
                    edit_address = alpha_col + str((rrdfI+2))
                    value = str(e).replace("'","").replace('"',"")
                    write_single_cell_to_gsheet(etl_workbook_id,sheet_name,edit_address,value)
        try:
            os.remove(local_folder + publish_file)
        except:
            file_not = 1

    value = str(datetime.datetime.now())
    write_single_cell_to_gsheet(etl_workbook_id, 'latest_scans', 'B3', value)
    # time.sleep(3*60)

# wrap in an error handler for the occasional timeout.
# while 1 != 0:
def file_scan_run():

    try:
        file_to_s3_scanner()
        print("file scan complete " + str(datetime.datetime.now()))
    except Exception as e:
        print(e)
        print("file scan failed " + str(datetime.datetime.now()))

