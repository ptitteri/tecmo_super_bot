import time
import json
import os
import pyperclip as pc
import datetime
from github import Github
import pandas as pd
from aws_tools.console_tools import push_local_file_to_s3, pull_s3_file_to_df, push_df_to_s3,get_s3_csv_dataframe
from etl_tools.web_automation_tools import start_chrome_session, web_command_wrapper
from google_tools.google_api import get_alpha_column_from_df, write_single_cell_to_gsheet, df_to_gsheet_simple, \
    pull_gsheet_data
from web_bots.bot_tools import click_link_with_name
from selenium.webdriver.common.keys import Keys
from etl_tools.looker_tools import download_looker_sql_runner
from etl_tools.error_email_notification import sot_bot_notification
from etl_tools.bot_run_logs import bot_run_logs
import platform
import pytz

# def scan_for_jobs():
#     etl_workbook_id = "1mMPZY53acyFcnm4qFjZdsTbhkBcq1VQfx_eMQGtTH0U"
#     sheet_name = 'etl_jobs_test'
#     chrome_profile = "/Users/Kiran.Kadlag/Library/Application Support/Google/Chrome/Profile 3"
#     run_requests_df = pull_gsheet_data(etl_workbook_id, sheet_name)
#     run_requests_df = run_requests_df[run_requests_df['reference_link'] != ""]
#     active_run_requests_df = run_requests_df[run_requests_df.run_now == '1']
#     sql_runner_requests_df = active_run_requests_df[active_run_requests_df.reference_link_type == 'sql_runner']
#     git_link_requests_df = active_run_requests_df[active_run_requests_df.reference_link_type == 'github_link']  # new line to add in scanner

#     if len(sql_runner_requests_df) > 0:
#         # download_looker_sql_runner(chrome_profile,sql_runner_requests_df,etl_workbook_id,sheet_name)
#         #print("Pete's computer will run as normal")
#     if len(git_link_requests_df) > 0:  # new line to add in scanner
#         download_looker_git_link(chrome_profile, git_link_requests_df, etl_workbook_id, sheet_name)


def get_github_code(link):
    # github config file location
    cwd = os.getcwd()
    #bot_credentials_location = cwd + '\\github_tools\\git_config.json'
    bot_credentials_location = cwd + '/github_tools/git_config.json'
    with open(bot_credentials_location) as f:
      config = json.load(f)

    user_name = config['user_name']
    password = config['access_token']
    #os.chdir("/Users/Kiran.Kadlag/Documents/sot_tools")

    # create personal access token from github account
    git = Github(user_name, password)
    repo = git.get_repo("PillPack/sot_tools")  # no "/" at end of link
    content_link = link.split("master/")
    file_link = content_link[-1]

    raw_github_link = repo.get_contents(file_link)
    link_raw_code = raw_github_link.decoded_content.decode()

    return link_raw_code


def download_looker_git_link(chrome_profile, git_link_requests_df, etl_workbook_id, sheet_name, filetype='csv'):
    #local_folder = "C:\\Users\\peter.titterington\\Downloads\\"
    local_folder = "/Users/peteeti/Downloads/"
    local_file_path = 'not_established_yet'
    git_link_requests_df['orig_index'] = git_link_requests_df.index
    git_link_requests_df = git_link_requests_df.reset_index(drop=True)
    try:
        driver.close()
        print("prior driver closed")
    except:
        print("fresh driver available")
    try:
        driver = start_chrome_session(chrome_profile)
        driver.set_page_load_timeout(2000)
        dfI = 0

        for index in range(0, len(git_link_requests_df)):

            job_start_datetime = str(datetime.datetime.now())[:16]
            reference_link = git_link_requests_df['reference_link'][index]
            file_name = git_link_requests_df['file_name'][index]
            s3_bucket = git_link_requests_df['s3_bucket'][index]
            s3_path = git_link_requests_df['s3_path'][index]
            replace_flag = git_link_requests_df['replace_existing'][index]
            type = git_link_requests_df['type'][index]
            gsheet_id = git_link_requests_df['gsheet_id'][index]
            gsheet_tab = git_link_requests_df['gsheet_tab'][index]
            gsheet_range_to_populate = git_link_requests_df['gsheet_range_to_populate'][index]
            local_publish_path = git_link_requests_df['local_publish_path'][index]

            alpha_col = get_alpha_column_from_df(git_link_requests_df, 'error_code')
            edit_row = git_link_requests_df['orig_index'][dfI]
            edit_address = alpha_col + str((edit_row + 2))
            value = "...SotETL is working on it"
            write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

            tries = 60

            if dfI == 0:
                looker_link = 'https://pillpack.looker.com/'
                web_command_wrapper(driver.get(looker_link), 10, tries)
                ## maybe check to see if this button is present or something
                #check to see if this login is required
                try:
                    web_command_wrapper(driver.find_element('xpath','//*[@id="login-submit"]').click(), 20, 3)
                except:
                    print("bot is already logged in")

            looker_link = "https://pillpack.looker.com/sql/"
            web_command_wrapper(driver.get(looker_link), 10, tries)

            link_dict = [{'link_name': 'database', 'link_type': 'xpath',
                          'link': '//*[@id="lk-nav"]/div/div[2]/div/div[3]/select'},
                         {'link_name': 'setting_gear', 'link_type': 'xpath',
                          'link': '//*[@id="lk-title"]/div[3]/div[2]'},
                         {'link_name': 'download_option', 'link_type': 'xpath',
                          'link': '//*[@id="lk-layout-ng"]/ul/li[1]'},
                         {'link_name': 'file_format', 'link_type': 'xpath',
                          'link': '//*[@id="sql-export-modal-format"]/option[3]'},
                         {'link_name': 'download_button', 'link_type': 'xpath',
                          'link': '//*[@id="lk-layout-ng"]/div[1]/div/div/lk-sql-runner-download-modal/div[3]/button[2]'}]

            # select database
            link_name = 'database'
            field = click_link_with_name(link_name, link_dict, driver)
            database_name = "snowflake-production"
            field.send_keys(database_name)

            print ("database selected ")
            # copy github raw link code
            git_raw_code = get_github_code(reference_link)
            print ("git raw code imported")
            pc.copy("empty string")
            print ("empty string loaded to clipboard")
            pc.copy(git_raw_code)

            # # copy code to text area
            # web_command_wrapper(driver.find_element_by_class_name('ace_text-input').send_keys(Keys.CONTROL + "a"), 20,
            #                     tries)
            # web_command_wrapper(driver.find_element_by_class_name('ace_text-input').send_keys(Keys.CONTROL + 'v'), 20,
            #                     tries)
            # copy code to text area
            web_command_wrapper(driver.find_element_by_class_name('ace_text-input').send_keys(Keys.COMMAND + "a"), 20,
                                tries)
            web_command_wrapper(driver.find_element_by_class_name('ace_text-input').send_keys(Keys.COMMAND + 'v'), 20,
                                tries)
            pc.copy("short string") # just to clear the contents for later
            # Enable script to click on the gear
            link_name = 'setting_gear'
            field = click_link_with_name(link_name, link_dict, driver)

            # Dropdown to select download option
            link_name = 'download_option'
            field = click_link_with_name(link_name, link_dict, driver)

            # select CSV from the options
            link_name = 'file_format'
            field = click_link_with_name(link_name, link_dict, driver)

            # Download the csv
            link_name = 'download_button'
            field = click_link_with_name(link_name, link_dict, driver)

            ##Enable script to start the file download process
            dfI = dfI + 1

            # check for files that are downloading
            tS = 0
            download_found = 0

            print("waiting up to 20 minutes for queries to complete")
            while tS <= (120) and download_found == 0:
                print(tS)
                time.sleep(10)
                file_list = os.listdir(local_folder)
                download_found = 1
                tS = tS + 1
                for f in file_list:
                    if f.find('crdownload') != -1:
                        download_found = 0

                    current_url = driver.current_url
                    file_unique_chars = current_url.split('/')[-1]
                    # rename file after complete download
                    if f.find(file_unique_chars) != -1 and f.find('crdownload') == -1:
                        #os.chdir(local_folder)
                        os.rename(local_folder + f, local_folder+file_name + '.csv')
                        # os.chdir("/Users/Kiran.Kadlag/Documents/sot_tools/")

            print(file_name + '.csv' + ' downloaded successfully')

            # Write output to Gsheet and S3
            local_file_path = local_folder + file_name + '.csv'
            pub_df = pd.read_csv(local_file_path)

            if type == 'simple_gsheet_import':
                if len(pub_df) > 0:
                    tz = pytz.timezone('US/Pacific')
                    pub_df['publish_time'] = str(datetime.datetime.now(tz))[:16]
                    header_range = gsheet_tab + "!" + gsheet_range_to_populate
                    df_to_gsheet_simple(gsheet_id, header_range, pub_df, delete_input=True)
                    print('G-sheet updated successfully')

            if type == 'publish_locally':
                if replace_flag == 'add_timestamp':
                    file_stamp = str(datetime.datetime.now())[:19].replace(":", "-").replace(" ", "_") + "_bot_time"
                else:
                    file_stamp = ""

                if platform.platform().lower().find('macos') != -1:
                    local_publish_path = local_publish_path.replace('\\','/')
                    local_path = local_publish_path + '/' + file_name + file_stamp + '.csv'
                    print(local_publish_path)
                elif platform.platform().lower().find('windows') != -1:
                    local_publish_path = local_publish_path.replace('/', '\\')
                    local_path = local_publish_path + '\\' + file_name + file_stamp + '.csv'
                    print(local_publish_path)

                if len(pub_df) > 0:
                    if not os.path.exists(local_publish_path):
                        os.mkdir(local_publish_path)
                    pub_df['publish_time'] = str(datetime.datetime.now())[:16]
                    pub_df.to_csv(local_path,encoding='utf-8',index=False)
                    print('file downloaded locally')
            else:
                if replace_flag == 'add_timestamp':
                    file_stamp = str(datetime.datetime.now())[:19].replace(":", "-").replace(" ", "_") + "_bot_time"
                else:
                    file_stamp = ""
                s3_file_name = file_name + file_stamp + ".csv"
                # if the path doesn't exist, create it
                push_local_file_to_s3(s3_bucket, s3_path, s3_file_name, local_file_path)
                print('S3 bucket updated successfully')

            # Update last_run and error_code
            return_code_update(local_folder, local_file_path, file_name, etl_workbook_id, sheet_name, reference_link,
                               job_start_datetime, message="success")

            # quick clean up in case old files are lying around
            for f in file_list:
                if f.find(file_unique_chars) != -1:
                    try:
                        os.remove(local_folder+f)
                    except:
                        print (f + " already removed")

        driver.close()
    except Exception as e:
        try:
            driver.close()
            print("prior driver closed")
        except:
            print("fresh driver available")
        print(e)
        return_code_update(local_folder, local_file_path, file_name, etl_workbook_id, sheet_name, reference_link,
                           job_start_datetime, message=e)



def return_code_update(local_folder, local_file_path, file_name, etl_workbook_id, sheet_name, reference_link,
                       job_start_datetime, message):
    run_requests_df = pull_gsheet_data(etl_workbook_id, sheet_name)

    try:
        #1==1
        #os.chdir(local_folder)
        os.remove(local_file_path)
        #os.chdir("/Users/Kiran.Kadlag/Documents/sot_tools/")
    except:
        print(file_name + '.csv' + " already deleted")

    try:
        rrdfI = 0
        for file in run_requests_df['file_name']:
            if file == file_name:
                if message == "success":
                    alpha_col = get_alpha_column_from_df(run_requests_df, 'last run at')
                    edit_address = alpha_col + str((rrdfI + 2))
                    tz = pytz.timezone('US/Pacific')
                    value = str(datetime.datetime.now(tz))[:16]
                    write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                    alpha_col = get_alpha_column_from_df(run_requests_df, 'error_code')
                    edit_address = alpha_col + str((rrdfI + 2))
                    value = "(none)"
                    write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                    alpha_col = get_alpha_column_from_df(run_requests_df, 'Manually Re-Trigger')
                    edit_address = alpha_col + str((rrdfI + 2))
                    value = 0
                    write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                    bot_run_logs(sheet_name, reference_link, job_start_datetime, error_message=value)

                else:
                    print("file_scanner_failed")
                    alpha_col = get_alpha_column_from_df(run_requests_df, 'last run at')
                    edit_address = alpha_col + str((rrdfI + 2))
                    tz = pytz.timezone('US/Pacific')
                    value = str(datetime.datetime.now(tz))[:16]
                    write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)
                    alpha_col = get_alpha_column_from_df(run_requests_df, 'error_code')
                    edit_address = alpha_col + str((rrdfI + 2))
                    value = str(message).replace("'", "").replace('"', "")
                    write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                    alpha_col = get_alpha_column_from_df(run_requests_df, 'Manually Re-Trigger')
                    edit_address = alpha_col + str((rrdfI + 2))
                    value = 0
                    write_single_cell_to_gsheet(etl_workbook_id, sheet_name, edit_address, value)

                    bot_run_logs(sheet_name, reference_link, job_start_datetime, error_message=value)
                    sot_bot_notification(sheet_name, reference_link, job_start_datetime, message=value)
            rrdfI += 1
    except Exception as e:
        print(e)

# # set scanner to run every hour or so on a forever loop
# while 1 > 0:
#     try:
#         scan_for_jobs()
#         print("query scan completed " + str(datetime.datetime.now()))
#     except:
#         print("scan failed " + str(datetime.datetime.now()))

#     time.sleep(5 * 60)
