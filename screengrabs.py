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


w = WindowMgr()
w.find_window_wildcard(".*Nestopia*")
w.dimensions()
#w.set_foreground()
#print("waiting")
#time.sleep(3)
#press_right(180)

def process_image(original_image):
    processed_image = cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
    processed_image = cv2.Canny(processed_image,threshold1=200,threshold2=300)
    return processed_image

    
    
last_time = time.time()
while (True):
    #grabs a screenshot
    screenshot = np.array(ImageGrab.grab(bbox=w._dims))
    
#   #this takes a while to do so it's commented out
#    printscreen_numpy= np.array(printscreen_pil.getdata(),dtype='uint8') \
#    .reshape((printscreen_pil.size[1],printscreen_pil.size[0],3))s
    processed_image = process_image(screenshot)
    print ("snapshot took {} seconds".format(time.time()-last_time))
    last_time = time.time()
    ##show the print screen interpretation
    #cv2.imshow('window',cv2.cvtColor(screenshot,cv2.COLOR_BGR2RGB))
    cv2.imshow('window',processed_image)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
    