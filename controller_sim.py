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


def press_right(t):
    tI=0
    while tI<t:
        pydirectinput.keyDown('right')
        pydirectinput.press('x')
        time.sleep(0.2)
        if random.random() <0.5:
            pydirectinput.keyDown('down')
            pydirectinput.keyUp('down')
        else:
            pydirectinput.keyDown('up')
            time.sleep(0.2)
            pydirectinput.keyUp('up')
        print("pressed ->")
        tI= tI + 1
        print (tI)

w = WindowMgr()
w.find_window_wildcard(".*Nestopia*")
dims = w.dimensions
w.set_foreground()

print("waiting")
time.sleep(3)
press_right(120)






    

