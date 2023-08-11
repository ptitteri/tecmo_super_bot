# -*- coding: utf-8 -*-

import time
from etl_tools.web_automation_tools import start_chrome_session,web_command_wrapper
from selenium.webdriver.support.ui import Select
from aws_tools.console_tools import get_s3_file_list,get_s3_csv_dataframe,delete_s3_file
from etl_tools.general_etl_tools import body_range_calculator
from google_tools.google_api import write_df_to_gsheet,get_alpha_column_from_df,write_single_cell_to_gsheet
from etl_tools.error_email_notification import sot_bot_notification
from etl_tools.bot_run_logs import bot_run_logs
import io
import datetime
import os
import pytz
from selenium.webdriver.common.by import By

def download_looker_sql_runner(chrome_profile,sql_runner_requests_df,etl_workbook_id,etl_sheet_name,filetype='csv'):
    sql_runner_requests_df['orig_index'] = sql_runner_requests_df.index
    sql_runner_requests_df = sql_runner_requests_df.reset_index(drop=True)
    try:
        driver.close()
        print ("prior driver closed")
    except:
        print ("fresh driver available")
    try:
        driver = start_chrome_session(chrome_profile)
        driver.set_page_load_timeout(1000)
        ##SQL Runner link for each query
        dfI = 0
        for link in sql_runner_requests_df['reference_link']:
            job_start_datetime = str(datetime.datetime.now())[:16]
            alpha_col = get_alpha_column_from_df(sql_runner_requests_df,'error_code')
            edit_row = sql_runner_requests_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row+2))
            value = "...SotETL is working on it"
            write_single_cell_to_gsheet(etl_workbook_id,etl_sheet_name,edit_address,value)


            tries = 60

            #naviagte to the link
            #go to looker first
            if dfI == 0:
                looker_link = 'https://pillpack.looker.com/'
                web_command_wrapper(driver.get(looker_link),60,tries)
                #web_command_wrapper(driver.find_element_by_xpath('//*[@id="login-submit"]').click(),20,tries)

            web_command_wrapper(driver.get(link),60,tries)
            
            ##Enable script to click on the gear
            web_command_wrapper(
                driver.find_element(By.CLASS_NAME,'lk-icon-gear').click()
                ,20,tries)

            #Dropdown to select download option
            web_command_wrapper(
                driver.find_element(By.CLASS_NAME,'dropdown-alt').click()
                ,20,tries)

            #select CSV from the options
            web_command_wrapper(
                Select(driver.find_element(By.ID,'sql-export-modal-format')).select_by_visible_text('CSV')
                ,20,tries)
            #Download the csv
            web_command_wrapper(
                driver.find_element(By.XPATH,'//button[text()="Download"]').click()
                ,1,tries)
            ##Enable script to start the file download process
            dfI = dfI + 1

            #write logs in s3 bucket
            bot_run_logs(etl_sheet_name, link, job_start_datetime, '(none)')

        print ("waiting up to 20 minutes for queries to complete")
        #check for files that are downloading
        #local_folder = "C:\\Users\\peter.titterington\\Downloads\\"
        local_folder = "/Users/peteeti/Downloads/"

        tS = 0
        download_found = 0

        while tS <= (120) and download_found == 0:
            print (tS)
            time.sleep(10)
            file_list = os.listdir(local_folder)
            download_found = 1
            for f in file_list:
                if f.find('crdownload') != -1:
                    download_found = 0
            tS = tS + 1
        print ("... time's up")
        driver.close()
    except Exception as e:
        print (e)
        error_message = str(e).replace("'", "").replace('"', "")
        bot_run_logs(etl_sheet_name, link, job_start_datetime, error_message)
        sot_bot_notification(etl_sheet_name, link, job_start_datetime,error_message)
        driver.close()

def s3_looks_to_gsheet(request_df,etl_workbook_id,etl_sheet_name,delete_old=False):


    #capture the original index values
    request_df['orig_index'] = request_df.index
    request_df = request_df.reset_index(drop=True)
    dfI = 0
    for s3_bucket in request_df.s3_bucket:
        try:
            alpha_col = get_alpha_column_from_df(request_df,'error_code')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row+2))
            value = "...PetETL is working on it"
            write_single_cell_to_gsheet(etl_workbook_id,etl_sheet_name,edit_address,value)

            s3_bucket = request_df['s3_bucket'][dfI]
            s3_path = request_df['s3_path'][dfI]
            s3_file_name = request_df['file_name'][dfI]
            gsheet_id = request_df['gsheet_id'][dfI]
            gsheet_tab = request_df['gsheet_tab'][dfI]
            gsheet_range_to_populate = request_df['gsheet_range_to_populate'][dfI]

            #get the latest s3 object matching this publish event
            latest_file_json = get_latest_s3_published_look_name(s3_bucket,s3_path,s3_file_name,delete_old=delete_old)
            #push the latest file back to gheets
            s3_read_path = latest_file_json['Key']
            #get as dataframe first
            df = get_s3_csv_dataframe(s3_bucket,s3_read_path)
            file_last_modified = str(latest_file_json['LastModified'])[:16]
            df['last_modified_utc'] = file_last_modified
            try:
                #gets rid of an auto-generated index column
                df = df.drop("Unnamed: 0",axis=1)
            except:
                no_index=1
            header_range =gsheet_tab  +"!" + gsheet_range_to_populate
            body_range = body_range_calculator(header_range)
            write_df_to_gsheet(gsheet_id,header_range,body_range,df)
            #write the last updated time back to master
            alpha_col = get_alpha_column_from_df(request_df,'last run at')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row+2))
            tz = pytz.timezone('US/Pacific')
            value = str(datetime.datetime.now(tz))[:16]
            write_single_cell_to_gsheet(etl_workbook_id,etl_sheet_name,edit_address,value)

            alpha_col = get_alpha_column_from_df(request_df,'error_code')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row+2))
            value = "(none)"
            write_single_cell_to_gsheet(etl_workbook_id,etl_sheet_name,edit_address,value)

            alpha_col = get_alpha_column_from_df(request_df, 'Manually Re-Trigger')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row + 2))
            value = 0
            write_single_cell_to_gsheet(etl_workbook_id, etl_sheet_name, edit_address, value)


        except Exception as e:
            #write the error message back to the main sheet
            alpha_col = get_alpha_column_from_df(request_df,'error_code')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row+2))
            value = str(e).replace("'","").replace('"',"")
            write_single_cell_to_gsheet(etl_workbook_id,etl_sheet_name,edit_address,value)


        dfI = dfI + 1





def get_latest_s3_published_look_name(s3_bucket,s3_path,s3_file_name,delete_old=False):
    file_list = get_s3_file_list(s3_bucket,s3_path+s3_file_name)
    fI =0
    for f in file_list:
        return_object = ""
        mod_date_check = f['LastModified']
        if fI ==0:
            mod_date = mod_date_check
            return_object = f
        else:
            if mod_date_check > mod_date :
                mod_date = mod_date_check
                return_object = f
    if delete_old == True:
        for f in file_list:
            mod_date_check = f['LastModified']
            file_path = f['Key']
            if mod_date > mod_date_check:
                # delete the older version of the file
                delete_s3_file(s3_bucket,file_path)
                print (file_path + " deleted...")

    return return_object
