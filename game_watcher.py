# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 10:02:22 2020

@author: ptitteri
"""

"""

stolen liberally from https://www.youtube.com/watch?v=ks4MPfMq8aQ
ep2 cv2 basics

next steps:
capture game situation in a log
measure the success of each play where 
    1st down = 20
    touchdown = 100
    + yardage gained/lost
capture the success in the log as well as the play called
capture the status of each defensive and offensive player in a json


"""
import boto3
from aws_tools.console_tools import *
import numpy as np
import pyscreenshot
import cv2
import copy
from window_manager import WindowMgr
from PIL import ImageGrab
import time
import pytesseract
from pytesseract import pytesseract
from sample_text_grab import read_screen_text
from datetime import datetime
from general_tools.log_tools import *
from image_capture.image_tools import *
from general_tools.text_interpretation_tools import condition_checker_situation_check
from controller_sim import save_state,call_random_play,bring_window_to_top
#read text example: https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/

# #to read log file in powershell Get-Content C:\Users\ptitt\Documents\GitHub\tecmo_super_bot\game_logs\game_log_live.txt -wait
path_to_tesseract = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
game_dict = [
    {'home_team':"bills"},
    {'away_team':"colts"},
    {'home_rb1':"thomas"},
    {'away_rb1':"bentle"}
    ]

def game_dict_return(key):
    for gd in game_dict:
        try:
            value = gd[key]
        except:
            donothing = 1
    return value

value = game_dict_return('home_team')
    

file_name = r'C:\Users\ptitt\Documents\GitHub\tecmo_super_bot\game_logs\game_log_live.csv'
last_time = time.time()
game_status = 'starting game'
write_to_log(file_name,[(game_status + ": snapshot took {} seconds".format(time.time()-last_time))],'w')

home_team = game_dict_return('home_team')
away_team = game_dict_return('away_team')
home_rb1 = game_dict_return('home_rb1')
away_rb1 = game_dict_return('away_rb1')
posession_status = 'unknown'
down = 'unknown'
yardline = 'unknown'

aws_bucket = 'tecmosuperbot-dev'
aws_path = 'images/'

log_file_headers = ["timestamp"
                    ,"play_id"
                    ,"game_status"
                    ,"play_call"
                    ,"posession_status_start"
                    ,"posession_status_end"
                    ,"yardline_start"
                    ,"yardline_end"
                    ,"down_start"
                    ,"down_end"
                    ,"yards_to_go_start"
                    ,"yards_to_go_end"
                    ,"home_score_start"
                    ,"away_score_start"
                    ,"home_score_end"
                    ,"away_score_end"
                    
    ]

#set log defaults
play_id = 'first_play'
game_status= 'first_play'
play_call= 'first_play'
posession_status_start= 'first_play'
posession_status_end= 'first_play'
yardline_start= 'first_play'
yardline_end= 'first_play'
down_start= 'first_play'
down_end= 'first_play'
yards_to_go_start= 'first_play'
yards_to_go_end= 'first_play'
home_score_start= 'first_play'
away_score_start= 'first_play'
home_score_end= 'first_play'
away_score_end= 'first_play'

play_id = 0

def create_log_data():
    strnow = str(datetime.now()).replace(":","-").replace(" ","_")
    log = [{    "timestamp": strnow
                ,"play_id":play_id
                ,"game_status":game_status
                ,"play_call":play_call
                ,"posession_status_start":posession_status_start
                ,"posession_status_end":posession_status_end
                ,"yardline_start":yardline_start
                ,"yardline_end":yardline_end
                ,"down_start":down_start
                ,"down_end":down_end
                ,"yards_to_go_start":yardline_start
                ,"yards_to_go_end":yardline_end
                ,"home_score_start":home_score_start
                ,"away_score_start":away_score_start
                ,"home_score_end":home_score_end
                ,"away_score_end":away_score_end
                }       
               ]             
    return log



while (True):

    screen_shot_type = 'Nestopia'
    window_type = ".*Nestopia"
    bring_window_to_top(window_type)
    screenshot = find_window_image(screen_shot_type)
    response = textract_response(screenshot)
    game_situation_text = game_situation_check(response)
    print(game_situation_text)
    text = extract_text_from_image(screenshot,psm=3).lower()

    #text = read_screen_text(processed_image)
    if text.find("select")!=-1 or text.find("ready")!= -1 :
        game_status = 'select play'
    else:
        game_status = 'not select play'
    
    if game_status == 'select play':  
       
        save_state()
        cc_check = False
        #scan the condition checker for game state
        ccI =0
        #capture the prior statuses before the new play is called
        posession_status_start = copy.deepcopy(posession_status_end)
        down_start = copy.deepcopy(down_end)
        yardline_start = copy.deepcopy(yardline_end)
        yards_to_go_start = copy.deepcopy(yards_to_go_end)  
        
        
        
        while cc_check == False and ccI <= 10:
            try:
                screen_shot_type = 'Condition'
                screenshot = find_window_image(screen_shot_type)
                response = textract_response(screenshot)
                situation_json = condition_checker_situation_check(response)
                posession_status_end = situation_json['posession']
                yards_to_go_end = situation_json['yards_to_go']
                down_end = situation_json['down']
                yardline_end = situation_json['yardline']
                cc_check = True
                print (situation_json)
            except:
                print ("couldn't see condition checker")
                ccI = ccI + 1
            game_pos_status = game_status + "-" + posession_status + " team has ball at the " + str(yardline) + " on " + str(down) + " down "
            
            if play_id == 0:
                write_mode = 'w'
            else:
                write_mode = 'a'

            csv_file_path = r'C:\Users\ptitt\Documents\GitHub\tecmo_super_bot\game_logs\game_log_live3.csv' 
            # Replace with the desired path for the CSV file
            log_data = create_log_data()
            write_to_csv(log_file_headers,log_data, csv_file_path,write_mode)
            
        play_status = 0 #a play has not yet been called
        print ("calculating perfect play")
        call_random_play()
        time.sleep(3) #wait 3 seconds for the play to get called and executed
        play_status = 1 # a play has been called
        play_id += 1 #add one to a variable
        #capture the image for ML identification

    # #show the print screen interpretation
    # cv2.imshow('window',screenshot)
    # if cv2.waitKey(25) & 0xFF == ord('q'):
    #     cv2.destroyAllWindows()
    #     break
