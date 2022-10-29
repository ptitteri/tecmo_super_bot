# -*- coding: utf-8 -*-
"""
Created on Sun Nov 15 10:02:22 2020

@author: ptitteri
"""

"""

stolen liberally from https://www.youtube.com/watch?v=ks4MPfMq8aQ
ep2 cv2 basics
"""
import numpy as np
import pyscreenshot
import cv2
from window_manager import WindowMgr
from PIL import ImageGrab
import time
import pytesseract
from pytesseract import pytesseract
from sample_text_grab import read_screen_text
from datetime import datetime
#import tesseract
#read text example: https://www.geeksforgeeks.org/text-detection-and-extraction-using-opencv-and-ocr/

#to read log file in powershell Get-Content C:\Users\ptitt\Documents\GitHub\tecmo_super_bot\game_logs\game_log_live.txt -wait
w = WindowMgr()
w.find_window_wildcard(".*Nestopia*")
w.dimensions()
#w.set_foreground()
#print("waiting")
#time.sleep(3)
#press_right(180)

game_dict = [
    {'home_team':"OILERS"},
    {'away_team':"JETS"},
    {'home_rb1':"WHITE"},
    {'away_rb1':"THOMAS"}
    ]

def game_dict_return(key):
    for gd in game_dict:
        try:
            value = gd[key]
        except:
            donothing = 1
    return value

value = game_dict_return('home_team')
    
#define where tesseract lives
path_to_tesseract = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
#Point tessaract_cmd to tessaract.exe
pytesseract.tesseract_cmd = path_to_tesseract
def process_image(original_image):
    #color
    #processed_image = cv2.cvtColor(original_image,cv2.COLOR_BGR2RGB)

    #B/W only
    processed_image = cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
    #lines only
    #processed_image = cv2.Canny(original_image,threshold1=200,threshold2=300)
    #parse out text from image
    #text = read_screen_text(processed_image)
    return processed_image
    #return original_image
    
file_name = r'C:\Users\ptitt\Documents\GitHub\tecmo_super_bot\game_logs\game_log_live'
def write_to_log(file_name,lines,mode):
    with open(file_name + '.txt', mode) as f:
        for line in lines:
            f.write('\n'.join(lines))
            f.write('\n')


last_time = time.time()
game_status = 'starting game'
write_to_log(file_name,[(game_status + ": snapshot took {} seconds".format(time.time()-last_time))],'w')

home_team = game_dict_return('home_team')
away_team = game_dict_return('away_team')
home_rb1 = game_dict_return('home_rb1')
away_rb1 = game_dict_return('away_rb1')
posession_status = 'unknown'

while (True):
    #grabs a screenshot
    #print (game_status + ": snapshot took {} seconds".format(time.time()-last_time))
    screenshot = np.array(ImageGrab.grab(bbox=w._dims))
    
    #simple approach
    #text = pytesseract.image_to_string(screenshot)
    
#   #this takes a while to do so it's commented out
#    printscreen_numpy= np.array(printscreen_pil.getdata(),dtype='uint8') \
#    .reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))s
    processed_image = process_image(screenshot)
    text = pytesseract.image_to_string(processed_image)
    text2 = pytesseract.image_to_string(screenshot)
    text3 = text+text2
    #text = read_screen_text(processed_image)
    if text3.find(home_team) != -1 or text3.find('SELECT') != -1 or text3.find('SELEGT') != -1 or text3.find('READY') != -1:
        game_status = 'select play'
        if text3.find(home_rb1) != -1:
            posession_status = 'P1'
        elif text3.find(away_rb1) != -1:
            posession_status = 'P2'
        else:
            possesion_status = 'unknown'
           
    else:
        game_status = 'play in progress'
    game_pos_status = game_status + "-" + posession_status + " has ball"
    log_message = (game_pos_status + ": snapshot took {} seconds".format(time.time()-last_time))
    print (log_message)
    #capture the image for ML identification
    strnow = str(datetime.now()).replace(":","-").replace(" ","_")
    cv2.imwrite("C:\\Users\\ptitt\Documents\\GitHub\\tecmo_super_bot\\image_capture\\" + strnow +" _" +game_pos_status + '.jpg',processed_image)
    write_to_log(file_name,[log_message],'a')
    last_time = time.time()
    #show the print screen interpretation
    cv2.imshow('window',processed_image)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    
    
    
    
    
#write to log file
# import pytesseract
# import cv2
# image_location = r"C:\Users\ptitt\Desktop\tecmoplays.jpg"
# img = cv2.imread(image_location)

# img = cv2.resize(img, (600, 360))
# text = pytesseract.tesseract_cmd.image_to_string(img)
# cv2.imshow('Result', img)
# cv2.waitKey(0)
