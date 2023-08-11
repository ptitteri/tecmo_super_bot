# -*- coding: utf-8 -*-

from etl_tools.web_automation_tools import click_web_element
import time
import json

# a few helper functions
def get_bot_credentials(bot_credentials_json,service_name):
    if bot_credentials_json == []:
        #bot_credentials_location = 'C:\\Users\\peter.titterington\\Documents\\GitHub\\sot_tools\\web_bots\\bot_credentials\\bot_credentials.json'
        bot_credentials_location = '/Users/Kiran.Kadlag/Documents/GitHub_bot/sot_tools/web_bots/bot_credentials/bot_credentials.json'
        with open(bot_credentials_location) as f:
            bot_credentials_json = json.load(f)
    for cred in bot_credentials_json:
        if cred['service_name'] == service_name:
            credentials = cred['service_credentials']
    return credentials

def get_link(link_dict,link_name,link_type):
    for ld in link_dict:
        if ld['link_name'] == link_name and ld['link_type']== link_type:
            link = ld['link']
    return link

def click_link_with_name(link_name,link_dict,driver):
    link = get_link(link_dict,link_name,'xpath')
    item = click_web_element(link,driver,element_type='xpath')
    return item

def accept_warning(driver):
    status = 0
    tries = 0
    while status == 0 and tries < 10:
        print("alert accept attempt " + str(tries))
        try:
            alert_obj = driver.switch_to.alert
            alert_obj.accept()
            status=1
        except Exception as e:
            print (str(e))
        time.sleep(1)
        tries = tries + 1