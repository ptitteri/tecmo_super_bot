# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 14:11:14 2020

@author: peter.titterington
"""
import pandas as pd
import numpy as np
import datetime
def add_time_dimensions(df,datetime_field,time_suffix="",iso_week=False,amazon_week=True,month=True,year=True):
    #set the field as datetime
    df[datetime_field] = df[datetime_field].astype('Datetime64')
    if iso_week == True:
        df['iso_week_num'+ time_suffix] = df[datetime_field].dt.week
    if amazon_week == True:
        df['amzn_week_num'+ time_suffix] = (df[datetime_field] + pd.Timedelta(days=1)).dt.week
    if month == True:
        df['month_num' + time_suffix] = df[datetime_field].dt.month
    if year == True:
        df['year' + time_suffix] = df[datetime_field].dt.year
    return df
        
    
        
        