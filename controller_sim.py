# -*- coding: utf-8 -*-
"""
Created on Sun Nov  1 14:52:39 2020

@author: ptitteri
"""

#controller simulation#
import pynput
from pynput.keyboard import Key, Controller
from window_manager import WindowMgr
import pydirectinput
import win32gui
import re
import time
import random


def tapoff(taps):
    t=1
    while t<= taps:
        pydirectinput.press('x')
        t= t + 1
        
def press_right(t):
    tI=0
    while tI<t:
        pydirectinput.keyDown('right')
        tapoff(1)
        time.sleep(0.2)
        tapoff(10)
        if random.random() <0.5:
            pydirectinput.keyDown('down')
            pydirectinput.keyUp('down')
        else:
            pydirectinput.keyDown('up')
            time.sleep(0.2)
            pydirectinput.keyUp('up')
        print("pressed ->")
        #pydirectinput.keyUp('right')
        tI= tI + 1
        print (tI)

w = WindowMgr()
w.find_window_wildcard(".*Nestopia*")
dims = w.dimensions
try:
    w.set_foreground()
except:
    print("window is already on top")
print("waiting")
time.sleep(3)

while 1==1:
    press_right(120)