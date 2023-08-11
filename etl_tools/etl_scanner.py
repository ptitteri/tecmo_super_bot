# -*- coding: utf-8 -*-


from google_tools.google_api import pull_gsheet_data,write_single_cell_to_gsheet
from etl_tools.looker_tools import download_looker_sql_runner,s3_looks_to_gsheet
import datetime
import time
from github_tools.github_connect import download_looker_git_link
etl_workbook_id ="1QuxVh5cUxVf8OMStVcgzNxVyNv3LBad_6nrCKtN-j_E"
sheet_name = 'etl_jobs'

def scan_for_jobs():
    run_requests_df = pull_gsheet_data(etl_workbook_id,sheet_name)
    run_requests_df = run_requests_df[run_requests_df['reference_link'] != ""]
    try:
        active_run_requests_df = run_requests_df[run_requests_df.run_now=='1']
        sql_runner_requests_df = active_run_requests_df[active_run_requests_df.reference_link_type == 'sql_runner']
        s3_look_to_gsheet_requests_df = active_run_requests_df[active_run_requests_df.reference_link_type == 'look_published']
        git_link_requests_df = active_run_requests_df[active_run_requests_df.reference_link_type == 'github_link']
    
        #first push the look s3 files to their respective gsheets
        if len(s3_look_to_gsheet_requests_df) > 0:
           s3_looks_to_gsheet(s3_look_to_gsheet_requests_df,etl_workbook_id,sheet_name,delete_old=True)
    
        #sql_link_list = sql_runner_requests_df.reference_link.tolist()
        #chrome_profile = "C:\\Users\\peter.titterington\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 1"
        chrome_profile = "/Users/peteeti/Library/Application Support/Google/Chrome/Profile 5"
        if len(sql_runner_requests_df) >0:
            download_looker_sql_runner(chrome_profile,sql_runner_requests_df,etl_workbook_id,sheet_name)
    
        if len(git_link_requests_df) > 0:  # new line to add in scanner
            download_looker_git_link(chrome_profile, git_link_requests_df, etl_workbook_id, sheet_name)

    
    except Exception as e:
        print (str(e))

    value = str(datetime.datetime.now())
    write_single_cell_to_gsheet(etl_workbook_id,'latest_scans','B2',value)

#set scanner to run every hour or so on a forever loop
def etl_scan_run():
    try:
        scan_for_jobs()
        print("etl scan completed " + str(datetime.datetime.now()))
    except Exception as e:
        print(str(e))
        print("etl failed " + str(datetime.datetime.now()))

