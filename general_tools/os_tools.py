# -*- coding: utf-8 -*-
"""
Created on Wed Sep  8 09:22:03 2021

@author: peter.titterington
"""

from wakepy import set_keepawake, unset_keepawake
import time

while 1 > 0:
    set_keepawake(keep_screen_awake=True)
    print ("screen set to awake, do it again in a bit")
    time.sleep(60)
    