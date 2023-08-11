from etl_tools.web_automation_tools import start_chrome_session,click_web_element
import time
import datetime
import json
import os
from aws_tools.console_tools import push_local_file_to_s3
from procurement.contracts.abc_contract.compile_prxo import compile_abc_prxo_and_catalogs
import copy


def abdc_sftp_pull_and_processing(detail_days_back=3):
    #set up a bot profile
    #chrome_profile = 'C:\\Users\\peter.titterington\\AppData\\Local\\Google\\Chrome\\User Data\\Profile 2'
    chrome_profile = r"/Users/peteeti/Library/Application Support/Google/Chrome/Profile 3"
    """
    #jobs to do:
    pull invoice files (trailing 3 days)
    pull catalog files (trailing 3 weeks)
    pull PRxO Daily XL files
    """
    #downloads_folder = "C:\\Users\\peter.titterington\\Downloads\\"
    downloads_folder = r"/Users/peteeti/Downloads/"

    from procurement.contracts.abc_contract.abc_supporting_data import files_to_pull
    files_to_pull = files_to_pull()
    #how far back to look
    
    #create list of files to look for    
    file_pull_list = []
    for file in files_to_pull:
        file_stub = file['file_stub']
        file_type = file['file_type']
        alternate_days_back = file['alternate_days_back']
        stub_suffix = file['stub_suffix']
        if alternate_days_back == None:
            days_back = detail_days_back
        else:
            days_back = alternate_days_back
            
        detail_date_end = datetime.datetime.now()
        detail_date_list = []
        dI = 0
        while dI < days_back:
            detail_date_list.append(str(detail_date_end - datetime.timedelta(days=dI))[:10])
            dI = dI + 1


        for date in detail_date_list:
            datetype = file['datetype']
            if datetype=='yyyy-mm-dd':
                date_string = date
            elif datetype=='mmddyyyy':
                date_string = str(date[5:7]+date[8:10]+date[:4])
            elif datetype=='mm.dd.yyyy':
                date_string = str(date[5:7]+"."+date[8:10]+"."+date[:4])
            elif datetype=='mm-dd-yy':
                date_string = str(date[5:7]+'-'+date[8:10]+'-'+date[2:4])
            elif datetype=='mm-dd-yyyy':
                date_string = str(date[5:7]+'-'+date[8:10]+'-'+date[0:4])

            if stub_suffix == 'date-time':
                file_name = file_stub + date_string
            else:
                file_name = file_stub + date_string + stub_suffix + file_type

            file_pull_list.append(file_name)
    

    #establish a web session
    try:
        driver.close()
    except:
        driver = start_chrome_session(chrome_profile)
    
    # a few helper functions
    def get_bot_credentials(bot_credentials_json,service_name):
        for cred in bot_credentials_json:
            if cred['service_name'] == service_name:
                credentials = cred['service_credentials']
        return credentials
    
    def get_link(link_dict,link_name,link_type):
        for ld in link_dict:
            if ld['link_name'] == link_name and ld['link_type']== link_type:
                link = ld['link']
        return link
    
    def click_link_with_name(link_name,link_dict):
        link = get_link(link_dict,link_name,'xpath')
        item = click_web_element(link,driver,element_type='xpath')

        return item
    
    #setup xpath dictionary
    link_dict = [
     {'link_name':'user_name','link_type':'xpath','link':'//*[@id="welcome_userName"]'}
     ,{'link_name':'password','link_type':'xpath','link':'//*[@id="welcome_password"]'}
     ,{'link_name':'login','link_type':'xpath','link':'//*[@id="welcome_submit"]'}
     ,{'link_name':'checkbox','link_type':'xpath','link':'//*[@id="fileDownload_fileChk"]'}
     ,{'link_name':'download_all','link_type':'xpath','link':'//*[@id="fileDownloadtolocal_submit"]'}
     ]

    #bot_credentials_location = 'C:\\Users\\peter.titterington\\Documents\\GitHub\\sot_tools\\web_bots\\bot_credentials\\bot_credentials.json'
    bot_credentials_location = r'C:\Users\peteeti\Documents\GitHub\sot_tools\web_bots\bot_credentials\bot_credentials.json'
    with open(bot_credentials_location) as f:
      bot_credentials_json = json.load(f)
    
    
    #fetch credentials
    abc_sftp_creds = get_bot_credentials(bot_credentials_json,'abc_sftp')
    abc_user_name = abc_sftp_creds['login']
    abc_pw = abc_sftp_creds['password']
    
    #navigate to the site
    abc_url = 'https://secure.amerisourcebergen.com/secureProject/jsp/Login.jsp'
    driver.get(abc_url)
    
    #enter "user name"
    link_name = 'user_name'
    field = click_link_with_name(link_name,link_dict)
    field.send_keys(abc_user_name)
    
    #enter password
    link_name = 'password'
    field = click_link_with_name(link_name,link_dict)
    field.send_keys(abc_pw)
    
    #click loginc
    link_name = 'login'
    item = click_link_with_name(link_name,link_dict)
    
    print ("giving the page a seconds to load...")
    time.sleep(5)
    
    print ("selecting all available files...")
    #click all the available boxes
    #items = driver.find_elements_by_xpath('//*[@id="fileDownload_fileChk"]')
    items = driver.find_elements('xpath','//*[@id="fileDownload_fileChk"]')
    extra_file_list = copy.deepcopy(file_pull_list)
    for item in items:
        try:
            item_value = item.get_attribute('value')
            if item_value in file_pull_list :
                item.click()
                print ("downloading " + item_value)
                link_name = 'download_all'
                download = click_link_with_name(link_name,link_dict)
                time.sleep(1)
                #unclick the button and get ready for the next one
                item.click()
                #give it a second to think
                time.sleep(5)
                #creating new list with only omit reports and non file pull list items
                extra_file_list.remove(item_value)
        except:
            failed_item = 1

    for item in items:
        try:
            item_value = item.get_attribute('value')
            for element in extra_file_list:
                if item_value.find(element) != -1:
                    print(item_value)
                    item.click()
                    print("downloading " + item_value)
                    link_name = 'download_all'
                    download = click_link_with_name(link_name, link_dict)
                    time.sleep(1)
                    # unclick the button and get ready for the next one
                    item.click()
                    # give it a second to think
                    time.sleep(5)
        except Exception as e:
            print(e)

    print ("give them a moment for pity's sake")
    time.sleep(60)
    driver.close()

    s3_bucket =  'pillpack-sot-procurement-support'
    s3_path = 'amerisource_bergen/'
    #now scan for the files and put them in their proper homes
    file_list = os.listdir(downloads_folder)
    for f in file_list:
        if f in file_pull_list:
            print (f)
            push_local_file_to_s3(s3_bucket,s3_path,f,downloads_folder + f)
            os.remove(downloads_folder + f)
    for f in file_list:
        for element in extra_file_list:
            if f.find(element) != -1:
                print(f)
                push_local_file_to_s3(s3_bucket, s3_path, f, downloads_folder + f)
                os.remove(downloads_folder + f)

    #compile the files for easy consumption
    compile_abc_prxo_and_catalogs()
    
    
    
#abdc_sftp_pull_and_processing(detail_days_back=2)
