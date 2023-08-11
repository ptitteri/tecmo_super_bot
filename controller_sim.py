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

#controller config
a = 'x'
b = 'z'
up = 'up'
down = 'down'
right = 'right'
left = 'left'
select = "'"
start = "enter"

play_choices = [
 {'name':'r1','controller_combo':[up,a]}
 ,{'name':'r2','controller_combo':[left,a]}
 ,{'name':'r3','controller_combo':[right,a]}
 ,{'name':'r4','controller_combo':[down,a]}
 ,{'name':'p1','controller_combo':[up,b]}
 ,{'name':'p2','controller_combo':[left,b]}
 ,{'name':'p3','controller_combo':[right,b]}
 ,{'name':'p4','controller_combo':[down,b]}
 ]

def bring_window_to_top(window = ".*Nestopia"):
    w = WindowMgr()
    w.find_window_wildcard(window)
    dims = w.dimensions
    try:
        w.set_foreground()
    except:
        print("window is already on top")
        
        
def tapoff(taps):
    bring_window_to_top()
    t=1
    while t<= taps:
        pydirectinput.press(a)
        t= t + 1
        
def press_right(t):
    bring_window_to_top()
    tI=0
    while tI<t:
        pydirectinput.keyDown(right)
        tapoff(1)
        time.sleep(0.2)
        tapoff(10)
        if random.random() <0.5:
            pydirectinput.keyDown(down)
            pydirectinput.keyUp(down)
        else:
            pydirectinput.keyDown(up)
            time.sleep(0.2)
            pydirectinput.keyUp(up)
        print("pressed ->")
        #pydirectinput.keyUp('right')
        tI= tI + 1
        print (tI)

def save_state():
    bring_window_to_top()
    pydirectinput.keyDown("shift")
    pydirectinput.press('1')
    pydirectinput.keyUp('shift')
    bring_window_to_top(window=".*Error")
    pydirectinput.press("enter")

    


def call_random_play():
    bring_window_to_top()
    play_call = random.randint(0,7)
    name = play_choices[play_call]['name']
    direction = play_choices[play_call]['controller_combo'][0]
    button = play_choices[play_call]['controller_combo'][1]
    print(name + " " + direction + " and " + button)
    #give the console a second to accept the input
    time.sleep(1)
    pydirectinput.keyDown(direction)
    pydirectinput.press(button)
    pydirectinput.keyUp(direction)
    
    


# print("waiting")
# time.sleep(3)

# while 1==1:
#     press_right(120)