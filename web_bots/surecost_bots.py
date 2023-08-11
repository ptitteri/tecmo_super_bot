# -*- coding: utf-8 -*-

from etl_tools.web_automation_tools import start_chrome_session,click_web_element
import pandas as pd
from aws_tools.console_tools import get_s3_file_list,get_s3_csv_dataframe,push_local_file_to_s3,get_xl_from_s3,push_df_to_s3
from web_bots.bot_tools import get_bot_credentials,get_link,click_link_with_name,accept_warning
from selenium.webdriver.common.keys import Keys
import json
import time
import datetime
import os
import pytz
"""
to do
#abstract out credentials!
"""

def remove_current_surecost_mf():
    #this is a web bot that removes the current surecost mf settings
    
    url = 'https://surecost.net/surecost/listFormularyOverrideGroups.do'
    #chrome_profile = '/Users/kirkad/Library/Application Support/Google/Chrome/Profile 5'
    chrome_profile = '/Users/peteeti/Library/Application Support/Google/Chrome/Profile 8'

    try:
        print("closing driver....")
        driver.close()
    except:
        driver = start_chrome_session(chrome_profile)
        # navigate to the site
    try:
        print("loading...")
        driver.get(url)
        os.wait(30)
    except Exception as e:
        print(e)


    link_dict = [
     {'link_name':'corporateAccount','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[2]/td[2]/input'},
     {'link_name':'user','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[3]/td[2]/input'},
     {'link_name':'pwd','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[4]/td[2]/input'},
     {'link_name':'login','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[5]/td[2]/input'},
     {'link_name':'delete1','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[1]/td[2]/a[2]/img'},
     {'link_name':'delete2','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[2]/td[2]/a[2]/img'},
     {'link_name':'delete3','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[3]/td[2]/a[2]/img'},
     {'link_name':'delete4','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[4]/td[2]/a[2]/img'},
     {'link_name':'delete5','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[5]/td[2]/a[2]/img'},
     {'link_name':'delete6','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[6]/td[2]/a[2]/img'},
     {'link_name':'delete7','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[7]/td[2]/a[2]/img'},
     {'link_name':'delete8','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[8]/td[2]/a[2]/img'},
     {'link_name':'delete9','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[9]/td[2]/a[2]/img'},
     {'link_name':'delete10','link_type':'xpath','link':'//*[@id="group"]/tbody/tr[10]/td[2]/a[2]/img'},
     {'link_name': 'logout', 'link_type': 'xpath','link': '/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/table/tbody/tr/td[5]/a'},

     ]
    edit_button_xpaths = [
    '//*[@id="group"]/tbody/tr[1]/td[2]/a[1]/img',
    '//*[@id="group"]/tbody/tr[2]/td[2]/a[1]/img',
    '//*[@id="group"]/tbody/tr[3]/td[2]/a[1]/img',
    ]
    delete_button_xpaths = [
    '//*[@id="group"]/tbody/tr[1]/td[2]/a[2]/img',
    '//*[@id="group"]/tbody/tr[2]/td[2]/a[2]/img',
    '//*[@id="group"]/tbody/tr[3]/td[2]/a[2]/img',
    ]


    #
    try:
        #login if needed
        #set up links to click

        cwd = os.getcwd()
        bot_credentials_location = cwd + '/web_bots/bot_credentials/bot_credentials.json'
        with open(bot_credentials_location) as f:
            bot_credentials_json = json.load(f)
        # fetch credentials
        creds = get_bot_credentials(bot_credentials_json, 'surecost_reports')
        corp_login = creds['corp_login']
        user = creds['login']
        pwd = creds['password']

        #login
        link_name = 'corporateAccount'
        field = click_link_with_name(link_name,link_dict,driver)
        field.send_keys(corp_login)
        #enter "user name"
        link_name = 'user'
        field = click_link_with_name(link_name,link_dict,driver)
        field.send_keys(user)
        
        #enter password
        link_name = 'pwd'
        field = click_link_with_name(link_name,link_dict,driver)
        field.send_keys(pwd)
        
        #login
        link_name = 'login'
        field = click_link_with_name(link_name,link_dict,driver)

    
    except Exception as e:
        print(str(e))
    
    #if already logged in
    try:
        driver.get(url)
        #clear existing groups
        d = 1
        while d <= 3:
            try:
                link_name = 'delete1'
                print (link_name)
                field = click_link_with_name(link_name,link_dict,driver)
                accept_warning(driver)
            except Exception as e:
                print(str(e))
            time.sleep(3)
            d = d+1
                
        
    except Exception as e:
        print(str(e))
        
    #close the brownser
    try:
        # logout
        link_name = 'logout'
        field = click_link_with_name(link_name, link_dict, driver)
        # close main window
        driver.close()
    except:
        print ("driver already closed")

def get_formulary_overrides_report():
    #this is a web bot that pulls the current formulary overrides and pushes them to a s3
    url = 'https://surecost.net/surecost/listFormularyOverrideGroups.do'
    chrome_profile = '/Users/peteeti/Library/Application Support/Google/Chrome/Profile 8'
    #chrome_profile = "/Users/kirkad/Library/Application Support/Google/Chrome/Profile 5"
    downloads_folder = '/Users/peteeti/Downloads/'
    #downloads_folder = '/Users/kirkad/Downloads/'
    #clear any files that have previously been downloaded
    file_list = os.listdir(downloads_folder)
    for f in file_list:
        if f.find("Formulary_Overrides") != -1:
            os.remove(downloads_folder + f)
    try:
        print("closing driver....")
        driver.close()
    except:
        driver = start_chrome_session(chrome_profile)
    #navigate to the site
    try:
        print("loading...")
        driver.get(url)
        os.wait(30)
    except Exception as e:
        print(e)

    link_dict = [
     {'link_name':'corporateAccount','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[2]/td[2]/input'},
     {'link_name':'user','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[3]/td[2]/input'},
     {'link_name':'pwd','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[4]/td[2]/input'},
     {'link_name':'login','link_type':'xpath','link':'/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[5]/td[2]/input'},
     {'link_name':'formulary_overrides_report','link_type':'xpath','link':'/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/div/form/table/tbody/tr[2]/td/table/tbody/tr[15]/td[5]/a/img'},
     {'link_name':'run_report','link_type':'xpath','link':'//*[@id="runReportBtn"]'},
     {'link_name': 'logout', 'link_type': 'xpath', 'link': '/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/table/tbody/tr/td[5]/a'},
     ]

    try:
        #login if needed
        #set up links to click

        cwd = os.getcwd()
        bot_credentials_location = cwd + '/web_bots/bot_credentials/bot_credentials.json'
        with open(bot_credentials_location) as f:
            bot_credentials_json = json.load(f)
        # fetch credentials
        creds = get_bot_credentials(bot_credentials_json, 'surecost_reports')
        corp_login = creds['corp_login']
        user = creds['login']
        pwd = creds['password']
        print(6)
        #login
        link_name = 'corporateAccount'
        field = click_link_with_name(link_name,link_dict,driver)
        field.send_keys(corp_login)
        #enter "user name"
        link_name = 'user'
        field = click_link_with_name(link_name,link_dict,driver)
        field.send_keys(user)
        
        #enter password
        link_name = 'pwd'
        field = click_link_with_name(link_name,link_dict,driver)
        field.send_keys(pwd)
        
        #login
        link_name = 'login'
        field = click_link_with_name(link_name,link_dict,driver)

        #navigate to the reports section
        driver.get("https://surecost.net/surecost/listReports.do")
        link_name = 'formulary_overrides_report'
        field = click_link_with_name(link_name,link_dict,driver)
        #download the current report for whole corp
        link_name = 'run_report'
        #switch to new window:
        driver.switch_to.window(driver.window_handles[1])
        field = click_link_with_name(link_name,link_dict,driver)
        #wait 10 seconds for the file to download
        time.sleep(20)

        #close download window
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        # logout
        link_name = 'logout'
        field = click_link_with_name(link_name, link_dict, driver)
        #close main window
        driver.close()

        datetime1 = datetime.datetime.now(pytz.timezone('US/Central'))
        file_name = 'Formulary_Overrides_' + str(datetime1)[:10].replace("-","") + ".xlsx"
        df = pd.read_excel(downloads_folder+file_name)
        os.remove(downloads_folder+file_name)
        
        return df
        
    except Exception as e:
        print(str(e))


def get_ppx_current_pricing():
    # this is a web bot that pulls the current formulary overrides and pushes them to a s3
    url = 'https://surecost.net/surecost/listFormularyOverrideGroups.do'
    #chrome_profile = "/Users/kirkad/Library/Application Support/Google/Chrome/Profile 5"
    chrome_profile = '/Users/peteeti/Library/Application Support/Google/Chrome/Profile 3'
    #downloads_folder = '/Users/kirkad/Downloads/'
    downloads_folder = '/Users/peteeti/Downloads/'

    # clear any files that have previously been downloaded
    file_list = os.listdir(downloads_folder)
    for f in file_list:
        if f.find("Vendor_Prices_Current_") != -1:
            os.remove(downloads_folder + f)
    try:
        print("closing driver....")
        driver.close()
    except:
        driver = start_chrome_session(chrome_profile)
    # navigate to the site
    try:
        print("loading...")
        driver.get(url)
        os.wait(30)
    except Exception as e:
        print(e)

    link_dict = [
        {'link_name': 'corporateAccount', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[2]/td[2]/input'},
        {'link_name': 'user', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[3]/td[2]/input'},
        {'link_name': 'pwd', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[4]/td[2]/input'},
        {'link_name': 'login', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[5]/td[2]/input'},
        {'link_name': 'current_pricing_xlsx', 'link_type': 'xpath',
        'link': '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/div/form/table/tbody/tr[2]/td/table/tbody/tr[43]/td[5]/a/img'},
        {'link_name': 'current_pricing_option', 'link_type': 'xpath', 'link': '/html/body/div/form/table/tbody/tr[1]/td[2]/select[2]'},
        {'link_name': 'ppx_option', 'link_type': 'xpath','link': '/html/body/div/form/table/tbody/tr[1]/td[2]/select[2]/option[6]'},
        {'link_name': 'run_report', 'link_type': 'xpath', 'link': '/html/body/div/form/table/tbody/tr[8]/td/input'},
        {'link_name': 'logout', 'link_type': 'xpath','link': '/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/table/tbody/tr/td[5]/a'},
    ]

    try:
        # login if needed
        # set up links to click

        cwd = os.getcwd()
        bot_credentials_location = cwd + '/web_bots/bot_credentials/bot_credentials.json'
        with open(bot_credentials_location) as f:
            bot_credentials_json = json.load(f)
        # fetch credentials
        creds = get_bot_credentials(bot_credentials_json, 'surecost_reports')
        corp_login = creds['corp_login']
        user = creds['login']
        pwd = creds['password']

        # login
        link_name = 'corporateAccount'
        field = click_link_with_name(link_name, link_dict, driver)
        field.send_keys(corp_login)
        # enter "user name"
        link_name = 'user'
        field = click_link_with_name(link_name, link_dict, driver)
        field.send_keys(user)

        # enter password
        link_name = 'pwd'
        field = click_link_with_name(link_name, link_dict, driver)
        field.send_keys(pwd)

        # login
        link_name = 'login'
        field = click_link_with_name(link_name, link_dict, driver)

        # navigate to the reports section
        driver.get("https://surecost.net/surecost/listReports.do")
        link_name = 'current_pricing_xlsx'
        field = click_link_with_name(link_name, link_dict, driver)

        driver.switch_to.window(driver.window_handles[1])
        link_name = 'current_pricing_option'
        field = click_link_with_name(link_name, link_dict, driver)

        link_name = 'ppx_option'
        field = click_link_with_name(link_name, link_dict, driver)

        # download the current report for whole corp
        link_name = 'run_report'
        # switch to new window:
        field = click_link_with_name(link_name, link_dict, driver)
        # wait 120 seconds for the file to download
        print("waiting for download to complete and closing first window")
        time.sleep(200)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        print("logging out surecost portal")
        # logout
        link_name = 'logout'
        field = click_link_with_name(link_name, link_dict, driver)
        # close main window
        driver.close()

        datetime1 = datetime.datetime.now(pytz.timezone('US/Central'))
        file_name = 'Vendor_Prices_Current_' + str(datetime1)[:10].replace("-", "") + ".xlsx"
        df = pd.read_excel(downloads_folder + file_name)
        df['source_file'] = file_name

        aws_bucket = 'pillpack-sot-looker-exports'
        aws_path = 'supply_chain/procurement_data/surecost_data/daily_purchases/current_pricing/'
        aws_file = 'current_pricing.csv'
        surecost_pricing_df = get_s3_csv_dataframe(aws_bucket, aws_path + aws_file)

        surecost_pricing_df_updated = surecost_pricing_df.append(df)
        surecost_pricing_df_updated = surecost_pricing_df_updated.drop_duplicates()
        push_df_to_s3(surecost_pricing_df_updated, aws_bucket, aws_path, aws_file)

        os.remove(downloads_folder + file_name)

        return df

    except Exception as e:
        print(str(e))


def surecost_pillpack_items_filled():
    # this is a web bot that pulls the current formulary overrides and pushes them to a s3
    url = 'https://surecost.net/surecost/listFormularyOverrideGroups.do'
    #chrome_profile = '/Users/kirkad/Library/Application Support/Google/Chrome/Profile 2'
    chrome_profile = '/Users/peteeti/Library/Application Support/Google/Chrome/Profile 3'
    #downloads_folder = '/Users/kirkad/Downloads/'
    downloads_folder = '/Users/peteeti/Downloads/'

    # clear any files that have previously been downloaded
    file_list = os.listdir(downloads_folder)
    for f in file_list:
        if f.find("Formulary_Overrides") != -1:
            os.remove(downloads_folder + f)
    try:
        print("closing driver....")
        driver.close()
    except:
        driver = start_chrome_session(chrome_profile)
        # navigate to the site
    try:
        print("loading...")
        driver.get(url)
        os.wait(30)
    except Exception as e:
        print(e)


    link_dict = [
        {'link_name': 'corporateAccount', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[2]/td[2]/input'},
        {'link_name': 'user', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[3]/td[2]/input'},
        {'link_name': 'pwd', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[4]/td[2]/input'},
        {'link_name': 'login', 'link_type': 'xpath',
         'link': '/html/body/div/form/table/tbody/tr[4]/td[2]/table/tbody/tr[5]/td[2]/input'},
        {'link_name': 'surecost_pillpack_items_filled', 'link_type': 'xpath',
         'link': '/html/body/table/tbody/tr[2]/td/table/tbody/tr/td/div/form/table/tbody/tr[2]/td/table/tbody/tr[7]/td[5]/a/img'},
        {'link_name': 'run_report', 'link_type': 'xpath', 'link': '//*[@id="runReportBtn"]'},
        {'link_name': 'date_range_dropdown', 'link_type': 'xpath',
         'link': '//*[@id="parameter(dateRange)"]/option[2]'},
        {'link_name': 'logout', 'link_type': 'xpath',
         'link': '/html/body/table/tbody/tr[1]/td/table/tbody/tr[2]/td[2]/table/tbody/tr/td[5]/a'},
    ]

    try:
        # login if needed
        # set up links to click

        cwd = os.getcwd()
        bot_credentials_location = cwd + '/web_bots/bot_credentials/bot_credentials.json'
        with open(bot_credentials_location) as f:
            bot_credentials_json = json.load(f)
        # fetch credentials
        #creds = get_bot_credentials(bot_credentials_json, 'surecost_reports')
        #updated for old credentials
        creds = get_bot_credentials(bot_credentials_json, 'surecost')
        corp_login = creds['corp_login']
        #   corp_login = creds['corp_login']
        user = creds['login']
        pwd = creds['password']

        # login
        link_name = 'corporateAccount'
        field = click_link_with_name(link_name, link_dict, driver)
        field.send_keys(corp_login)
        # enter "user name"
        link_name = 'user'
        field = click_link_with_name(link_name, link_dict, driver)
        field.send_keys(user)

        # enter password
        link_name = 'pwd'
        field = click_link_with_name(link_name, link_dict, driver)
        field.send_keys(pwd)

        # login
        link_name = 'login'
        field = click_link_with_name(link_name, link_dict, driver)

        # navigate to the reports section
        driver.get("https://surecost.net/surecost/listReports.do")
        link_name = 'surecost_pillpack_items_filled'
        field = click_link_with_name(link_name, link_dict, driver)

        # switch to new window:
        driver.switch_to.window(driver.window_handles[1])

        # select yesterday's report from date range
        link_name = 'date_range_dropdown'
        click_link_with_name(link_name, link_dict, driver)

        # download the current report for whole corp
        link_name = 'run_report'
        field = click_link_with_name(link_name, link_dict, driver)
        # wait 10 seconds for the file to download
        time.sleep(10)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

        print("logging out surecost portal")
        # logout
        link_name = 'logout'
        field = click_link_with_name(link_name, link_dict, driver)
        # close main window
        driver.close()

        yesterday = datetime.datetime.now(pytz.timezone('US/Central')) - datetime.timedelta(days=1)
        file_name = 'PillPack_Items_Filled_' + str(yesterday)[:10].replace("-", "")
        df = pd.read_excel(downloads_folder+file_name+'.xlsx')

        #move daily data to s3 bucket
        aws_bucket = 'pillpack-sot-procurement-support'
        aws_path = 'surecost_items_filled_report/'
        push_df_to_s3(df,aws_bucket,aws_path,file_name+'.csv', file_type='csv',include_header=True)
        os.remove(downloads_folder + file_name+'.xlsx')

    except Exception as e:
        print(str(e))
