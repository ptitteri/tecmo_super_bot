# scans the etl master for models to run

from google_tools.google_api import pull_gsheet_data, write_df_to_gsheet, get_alpha_column_from_df, \
    write_single_cell_to_gsheet
from aws_tools.console_tools import push_local_file_to_s3
import time
import pandas as pd
import os
import datetime
import string
from general_tools.mac_windows_path_edit import mac_windows_path_convert
import numpy as np
import pytz

etl_workbook_id = "1QuxVh5cUxVf8OMStVcgzNxVyNv3LBad_6nrCKtN-j_E"
sheet_name = 'model_runs'

cwd = os.getcwd()
keyword = ""

while 1 < 2:
    try:
        run_requests_df = pull_gsheet_data(etl_workbook_id, sheet_name)
        run_requests_df['orig_index'] = run_requests_df.index
        if keyword == "":
            model_requests_df = run_requests_df[(run_requests_df.run_now == '1')].reset_index(drop=True)
        else:
            model_requests_df = run_requests_df[(run_requests_df.model_file == keyword)].reset_index(drop=True)

        mI = 0
        for m in model_requests_df['model_file']:
            try:
                alpha_col = get_alpha_column_from_df(model_requests_df, 'bot_message')
                edit_row = model_requests_df['orig_index'][mI]
                edit_address = alpha_col + str((edit_row + 2))
                value = "...SotETL is working on it"
                write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                print("running " + m + "..........")
                m = mac_windows_path_convert(m)
                print(cwd + m)
                exec(open(cwd + m).read())

                # write back to the sheet to indicate the run was complete
                alpha_col = get_alpha_column_from_df(model_requests_df, 'last_updated')
                edit_row = model_requests_df['orig_index'][mI]
                edit_address = alpha_col + str((edit_row + 2))
                tz = pytz.timezone('US/Pacific')
                value = str(datetime.datetime.now(tz))[:16]
                write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)
                # write a non error message
                alpha_col = get_alpha_column_from_df(model_requests_df, 'bot_message')
                edit_row = model_requests_df['orig_index'][mI]
                edit_address = alpha_col + str((edit_row + 2))
                value = '(none)'
                write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)


            except Exception as e:
                print(e)
                alpha_col = get_alpha_column_from_df(model_requests_df, 'bot_message')
                edit_row = model_requests_df['orig_index'][mI]
                edit_address = alpha_col + str((edit_row + 2))
                value = str(e)
                write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                # write back to the sheet to indicate the run was complete
                alpha_col = get_alpha_column_from_df(model_requests_df, 'last_updated')
                edit_row = model_requests_df['orig_index'][mI]
                edit_address = alpha_col + str((edit_row + 2))
                tz = pytz.timezone('US/Pacific')
                value = str(datetime.datetime.now(tz))[:16]
                write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

            mI = mI + 1

    except Exception as e:
        print("gsheet connection failed")


    value = str(datetime.datetime.now())
    write_single_cell_to_gsheet(etl_workbook_id, 'latest_scans', 'B5', value)
    print("model scanner last check " + str(datetime.datetime.now()))
    time.sleep(60 * 5)
