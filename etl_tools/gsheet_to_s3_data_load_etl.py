from google_tools.google_api import pull_gsheet_data,get_alpha_column_from_df,write_single_cell_to_gsheet
from pandas_tools.df_columns_format import pandas_df_format
from aws_tools.console_tools import push_df_to_s3
import datetime
import pytz

etl_workbook_id ="1QuxVh5cUxVf8OMStVcgzNxVyNv3LBad_6nrCKtN-j_E"
sheet_name = 'gsheet_jobs'

def gsheet_to_s3_scanner():
    run_requests_df = pull_gsheet_data(etl_workbook_id, sheet_name)
    run_requests_df = run_requests_df[run_requests_df['gsheet_id'] != ""]
    active_run_requests_df = run_requests_df[run_requests_df.run_now=='1']
    if len(active_run_requests_df) > 0:
        gsheet_to_s3_data_load(active_run_requests_df,etl_workbook_id,sheet_name)

def gsheet_to_s3_data_load(request_df,etl_workbook_id,etl_sheet_name):
    try:
        request_df['orig_index'] = request_df.index
        request_df = request_df.reset_index(drop=True)
        dfI = 0
        for link in request_df['gsheet_id']:
            alpha_col = get_alpha_column_from_df(request_df, 'error_code')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row + 2))
            value = "...SotETL is working on it"
            write_single_cell_to_gsheet(etl_workbook_id, etl_sheet_name, edit_address, value)

            s3_bucket = request_df['s3_bucket'][dfI]
            s3_path = request_df['s3_path'][dfI]
            s3_file_name = request_df['file_name'][dfI]
            gsheet_id = request_df['gsheet_id'][dfI]
            gsheet_range = request_df['gsheet_range'][dfI]

            #read data from gsheet to pandas
            df = pull_gsheet_data(gsheet_id,gsheet_range)
            #convert all columns to lower case and remove comma and space
            df = pandas_df_format(df)

            push_df_to_s3(df, s3_bucket, s3_path, s3_file_name+'.csv', file_type="csv", include_header=True)

            # write back to the sheet to indicate the run was complete
            alpha_col = get_alpha_column_from_df(request_df, 'last run at')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row + 2))
            tz = pytz.timezone('US/Pacific')
            value = str(datetime.datetime.now(tz))[:16]
            write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)
            # write a non error message
            alpha_col = get_alpha_column_from_df(request_df, 'error_code')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row + 2))
            value = '(none)'
            write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

            alpha_col = get_alpha_column_from_df(request_df, 'Manually Re-Trigger')
            edit_row = request_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row + 2))
            value = 0
            write_single_cell_to_gsheet(etl_workbook_id, etl_sheet_name, edit_address, value)

            dfI = dfI + 1

    except Exception as e:
        alpha_col = get_alpha_column_from_df(request_df, 'error_code')
        edit_row = request_df['orig_index'][dfI]
        edit_address = alpha_col + str((edit_row + 2))
        value = str(e)
        write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

def gsheet_scan_run():
    try:
        gsheet_to_s3_scanner()
        print ("gsheet checks complete " + str(datetime.datetime.now()))
    except Exception as e:
        print (str(e))
        print("gsheet scan failed " + str(datetime.datetime.now()))
