# -*- coding: utf-8 -*-

## Import necessary python packages
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import time
import chromedriver_autoinstaller

def start_chrome_session(chrome_profile):
    chromedriver_autoinstaller.install()
    options = Options()
    ##Google chrome profile to store login cache to download file from link withouth having to re-authorize credentials

    #for windows
    options.add_argument("--start-maximized")
    #for MAC
    #options.add_argument("--kiosk")

    options.add_argument("user-data-dir=" + chrome_profile)
    driver = webdriver.Chrome(options=options)#,executable_path='/Users/Kiran.Kadlag/.wdm/drivers/chromedriver/mac64/103.0.5060.53/chromedriver')
    return driver

def web_command_wrapper(command_attempt,wait,attempts):
    time.sleep(wait)
    is_complete = 0
    i = 0
    while i < attempts and is_complete != 1:
        print ("trying command")
        try:
            command_attempt
            is_complete = 1
        except Exception as e:
            print (e)
            pass

        i = i + 1
    
def click_web_element(element_string,driver,element_type='xpath',return_item = 1):
    complete = 0
    iI = 0
    item=[]
    while complete == 0 and iI < 50:
        try:
            if element_type == 'xpath':
                print ("attempt " + str(iI) + " for " + element_string)
                #item = driver.find_element_by_xpath(element_string)
                item = driver.find_element(element_type, element_string)
                item.click()
                complete = 1
                
        except:
            print("attempt " + str(iI) + " failed for " + element_string)
        time.sleep(1)
        iI = iI + 1
    if return_item == 1:
        return item
        

    


        

