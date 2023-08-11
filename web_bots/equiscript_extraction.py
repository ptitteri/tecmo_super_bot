# -*- coding: utf-8 -*-


from etl_tools.web_automation_tools import start_chrome_session,click_web_element
import pandas as pd
import datetime
import os
from tzlocal import get_localzone
import time
import numpy as np
from aws_tools.console_tools import push_df_to_s3
from web_bots.bot_tools import get_bot_credentials,get_link,click_link_with_name
from selenium.webdriver.common.keys import Keys
import json

#file_folder = "C:\\Users\\peter.titterington\\Downloads\\"
file_folder = "/Users/Kiran.Kadlag/Downloads/"

def remove_files():
    file_list = os.listdir(file_folder)
    for f in file_list:
        if f.find("ClaimsExport") != -1:
            os.remove(file_folder + f)

remove_files()

# Script defined variables

file_name = "ClaimsExport.csv"
file_path = file_folder+ file_name
#chrome_profile = 'C:\\Users\\peter.titterington\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2'
chrome_profile = '"/Users/Kiran.Kadlag/Library/Application Support/Google/Chrome/Profile 3"'

#def pull_equiscript_340b():
try:
    link_dict = [
     {'link_name':'user_name','link_type':'xpath','link':'//*[@id="username"]'}
     ,{'link_name':'password','link_type':'xpath','link':'//*[@id="password"]'}
     ,{'link_name':'login','link_type':'xpath','link':'//*[@id="Login"]'}
     ,{'link_name':'claims','link_type':'xpath','link':'//*[@id="01rC0000000IcUr_Tab"]/a'}
     ,{'link_name':'claim_selector','link_type':'xpath','link':'//*[@id="j_id0:theForm:viewSelect"]'}
     ,{'link_name':'from_date','link_type':'xpath','link':'//*[@id="j_id0:theForm:fromDate"]'}
     ,{'link_name':'to_date','link_type':'xpath','link':'//*[@id="j_id0:theForm:toDate"]'}
     ,{'link_name':'go','link_type':'xpath','link':'//*[@id="j_id0:theForm:j_id15"]'}
     ,{'link_name':'download_results','link_type':'xpath','link':'//*[@id="j_id0:theForm:j_id17:myButtons"]/div[1]/input[2]'}
     ]
    cwd = os.getcwd()
    #bot_credentials_location = cwd + '\\web_bots\\bot_credentials\\bot_credentials.json'
    bot_credentials_location = cwd + '/web_bots/bot_credentials/bot_credentials.json'
    with open(bot_credentials_location) as f:
      bot_credentials_json = json.load(f)
    
    
    #fetch credentials
    creds = get_bot_credentials(bot_credentials_json,'equiscript_portal')
    user_name = creds['login']
    password = creds['password']

    # navigate to the site
    try:
        print("closing driver....")
        driver.close()
    except:
        driver = start_chrome_session(chrome_profile)
    # navigate to the site
    try:
        print("loading...")
        url = 'https://eq.force.com/RX/login'
        driver.get(url)
        os.wait(30)
    except Exception as e:
        print(e)


    #enter "user name"
    link_name = 'user_name'
    field = click_link_with_name(link_name,link_dict,driver)
    field.send_keys(user_name)
    
    #enter password
    link_name = 'password'
    field = click_link_with_name(link_name,link_dict,driver)
    field.send_keys(password)
    
    #log in
    link_name = 'login'
    field = click_link_with_name(link_name,link_dict,driver)
    time.sleep(5)
    
    #click claims
    link_name = 'claims'
    field = click_link_with_name(link_name,link_dict,driver)
    time.sleep(5)
    
    #click claims selector
    link_name = 'claim_selector'
    field = click_link_with_name(link_name,link_dict,driver)
    field.send_keys("All 340B Claims")
    time.sleep(5)

    #get trailing 60 days
    t60 = str(datetime.datetime.now() - datetime.timedelta(days=60))[:10]
    t60_keys = t60[5:7]+t60[8:10]+t60[:4]
    link_name = 'from_date'
    field = click_link_with_name(link_name,link_dict,driver)
    field.send_keys(Keys.LEFT)
    field.send_keys(Keys.LEFT)
    field.send_keys(t60_keys)
    
    today = str(datetime.datetime.now())[:10]
    today_keys = today[5:7]+today[8:10]+today[:4]
    link_name = 'to_date'
    field = click_link_with_name(link_name,link_dict,driver)
    field.send_keys(Keys.LEFT)
    field.send_keys(Keys.LEFT)
    field.send_keys(today_keys)
    
    #click run report
    link_name = 'go'
    field = click_link_with_name(link_name,link_dict,driver)
    time.sleep(30)
    
    #download report
    link_name = 'download_results'
    field = click_link_with_name(link_name,link_dict,driver)
    print ("downloading results....")
    time.sleep(60)

except Exception as e:
    print(str(e))

try:
    driver.close()
except:
    print ("driver already closed")

#def process_equiscript_340b(file_path):
local_timezone = get_localzone()
timestamptest = os.path.getmtime(file_path)
last_updated_timestamp = str(datetime.datetime.fromtimestamp(timestamptest))
last_updated_timestamp = last_updated_timestamp[:16]
# Load CSV into Dataframe
data = pd.read_csv(file_path,sep=',',index_col=False)
data['BIN_NUMBER'] = data['BIN Number'].astype(str).replace('\.0', '', regex=True)
data['BIN_NUMBER'] = data['BIN_NUMBER'].values.astype('str')
data['BIN_NUMBER'] = data['BIN_NUMBER'].str[:6]
data['BIN_NUMBER'] = data['BIN_NUMBER'].str.zfill(6)

data.drop(['Account Name', 'Date of Birth', 'BIN Number'], axis=1,inplace= True)
#data['File Date Time'] = last_updated_timestamp
#data.to_csv('/users/gavincleveland/Desktop/340b_file_2020-11-09.tsv',encoding='utf-8', index=False, sep='\t')
#data = data.replace(np.nan, 0)

s3_bucket =   "pillpack-sdaas-partner-data" 
s3_path = "equiscript/"
s3_file = "340b_file_" + str(last_updated_timestamp)[:10]
#data.to_csv(s3_file+".csv",index=False)
#data.to_csv(s3_file,index=False,sep='\t',encoding='UTF8')
push_df_to_s3(data,s3_bucket,s3_path,s3_file,file_type="tsv")

remove_files()
    
# pull_equiscript_340b()
# process_equiscript_340b(file_path)



    
