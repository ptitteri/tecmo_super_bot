import time
import os

import pandas as pd
from pandas_tools.df_columns_format import pandas_df_format
from aws_tools.console_tools import push_local_file_to_s3
from etl_tools.web_automation_tools import start_chrome_session, web_command_wrapper

#chrome_profile = 'C:\\Users\\peter.titterington\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2'
chrome_profile = "/Users/peteeti/Library/Application Support/Google/Chrome/Profile 3"

def download_fda_drugshortage_list(chrome_profile):

    try:
        driver = start_chrome_session(chrome_profile)
        driver.set_page_load_timeout(2000)
        dfI = 0
        tries = 60

        if dfI == 0:
            fda_link = 'https://www.accessdata.fda.gov/scripts/drugshortages/Drugshortages.cfm'
            web_command_wrapper(driver.get(fda_link), 10, tries)

        dfI = dfI + 1

        # check for files that are downloading
        #file_folder = "C:\\Users\\peter.titterington\\Downloads\\"
        file_folder = r"/Users/peteeti/Downloads/"
        tS = 0
        download_found = 0

        print("waiting up to 20 minutes for queries to complete")
        while tS <= (120) and download_found == 0:
            print(tS)
            time.sleep(10)
            file_list = os.listdir(file_folder)
            download_found = 1
            tS = tS + 1
            for f in file_list:
                if f.find('crdownload') != -1:
                    download_found = 0
                else:
                    file_unique_chars = "Drugshortages"
                    # rename file after complete download
                    if f.find(file_unique_chars) != -1 and f.find('crdownload') == -1:
                        print(file_unique_chars + '.csv' + ' downloaded successfully')

                        df = pd.read_csv(file_folder+'Drugshortages.csv')
                        df.columns = df.columns.str.strip()
                        data = pandas_df_format(df)
                        data = data.replace(',', '')
                        data['date_of_update'] = pd.to_datetime(data['date_of_update'])
                        data['initial_posting_date'] = pd.to_datetime(data['initial_posting_date'])
                        req_cols = ['generic_name', 'company_name', 'presentation',
                                    'type_of_update', 'date_of_update', 'availability_information',
                                    'related_information', 'resolved_note', 'reason_for_shortage',
                                    'therapeutic_category', 'status', 'initial_posting_date']
                        data = data[req_cols]
                        data.to_csv(file_folder+'Drugshortages.csv',encoding='utf-8',index=False)

                        s3_file_name = file_unique_chars + ".csv"
                        # if the path doesn't exist, create it
                        s3_bucket = 'pillpack-sdaas-partner-data'
                        s3_path = 'fda_current_drugs_shortage/'
                        local_file_path = file_folder + s3_file_name
                        push_local_file_to_s3(s3_bucket, s3_path, s3_file_name, local_file_path)

            #Delete file from system
            os.remove(local_file_path)
            print(s3_file_name+" deleted from local system")
            #Close chrome
            driver.close()
    except Exception as e:
        print(e)
        driver.close()

download_fda_drugshortage_list(chrome_profile)