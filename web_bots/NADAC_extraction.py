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

def nadac_file_download():
    #file_folder = "C:\\Users\\peter.titterington\\Downloads\\"
    file_folder = "/Users/Kiran.Kadlag/Downloads/"

    #clear out any previously downloaded files
    def remove_files():
        file_list = os.listdir(file_folder)
        for f in file_list:
            if f.find("national-average-drug-acquisition") != -1:
                os.remove(file_folder + f)

    remove_files()


    # Script defined variables
    file_stub = "national-average-drug-acquisition-cost-"
    #chrome_profile = 'C:\\Users\\peter.titterington\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2'
    chrome_profile = '/Users/Kiran.Kadlag/Library/Application Support/Google/Chrome/Profile 3'

    #
    try:
        #set up links to click
        link_dict = [
         {'link_name':'export','link_type':'xpath','link':'//*[@id="sidebarOptions"]/li[6]/a'},
         {'link_name':'csv','link_type':'xpath','link':'//*[@id="main-content"]/section/div/div[2]/div[1]/a'},

         ]

        try:
            print("closing driver....")
            driver.close()
        except:
            driver = start_chrome_session(chrome_profile)
        # navigate to the site
        try:
            print("loading...")
            url = 'https://data.medicaid.gov/dataset/d5eaf378-dcef-5779-83de-acdd8347d68e'  # 2021
            driver.get(url)
            os.wait(30)
        except Exception as e:
            print(e)

        #download file
        link_name = 'csv'
        field = click_link_with_name(link_name,link_dict,driver)

        # link_name = 'csv'
        # xpath = '//*[@id="controlPane_downloadDataset_14"]/form/div[3]/div[1]/div[4]/div/div/table/tbody/tr[1]/td/div/a'
        # field = click_web_element(xpath,driver,element_type='xpath')
        #field = click_link_with_xpath(xpath,link_dict,driver)

        #wait for N  minutes for the download to complete
        print ("waiting 2 minutes to download file...")
        time.sleep(60*2)


    except Exception as e:
        print(str(e))

    #close the brownser
    try:
        driver.close()
    except:
        print ("driver already closed")


    # Load CSV into Dataframe
    #find the file
    file_list = os.listdir(file_folder)
    for f in file_list:
        if f.find("national-average-drug-acquisition") != -1:
            file_name = f

    file_path = file_folder+ file_name
    local_timezone = get_localzone()
    timestamptest = os.path.getmtime(file_path)
    last_updated_timestamp = str(datetime.datetime.fromtimestamp(timestamptest))
    last_updated_timestamp = last_updated_timestamp[:16]


    data = pd.read_csv(file_path,sep=',',index_col=False)
    data['file_updated_at'] = last_updated_timestamp
    date_fields = ['As of Date','Effective_Date']
    for df in date_fields:
        data[df] = data[df].astype('Datetime64')

    data['As of Date'] = data['As of Date'].astype('str')

    s3_bucket =   "pillpack-sdaas-partner-data"
    s3_path = "NADAC/"
    s3_file = "nadac_data.txt"

    #data.to_csv(s3_file+".csv",index=False)
    #data.to_csv(s3_file,index=False,sep='\t',encoding='UTF8')
    push_df_to_s3(data,s3_bucket,s3_path,s3_file,file_type="tsv")
    remove_files()
    print ("NADAC extraction complete")


nadac_file_download()