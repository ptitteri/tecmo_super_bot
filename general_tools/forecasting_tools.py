# -*- coding: utf-8 -*-
"""
Created on Mon Dec 28 16:15:12 2020

@author: peter.titterington
"""
#holt winters forecast
import pandas as pd
#from matplotlib import pyplot as plt
from statsmodels.tsa.holtwinters import ExponentialSmoothing as HWES
import copy
import numpy as np

def add_forecast_to_df(df,forecast_metrics_list,test_periods,forecast_periods,sp=None,default_tweeks='nope'):
    
    freq = df.index.freq.name
    # file_path = "C:\\Users\\peter.titterington\\Desktop\\test_cars2.csv"
    # df = pd.read_csv(file_path, header=0, infer_datetime_format=True, parse_dates=[0], index_col=[0])
    # df.index.freq = 'MS'
    #try some holt winters as a start:
        #https://towardsdatascience.com/holt-winters-exponential-smoothing-d703072c0572
    full_df = copy.deepcopy(df)
    for metric in forecast_metrics_list:
        try:
            metric_df = df[metric].replace(np.nan,0)
            metric_df_trimmed = find_forecast_start(metric_df,tperiods=9,stdevcount=1)
            metric_df_trimmed.index.freq=freq
            periods = len(metric_df_trimmed)
            if periods < test_periods:
                test_periods = periods
            forecast_output_json = forecast_model_selection(metric_df_trimmed,test_periods,forecast_periods,sp=sp,tweeks=default_tweeks)
            output_df = forecast_output_json['output_df']
            full_df = pd.merge(full_df,output_df,how='outer',left_index=True,right_index=True)
        except Exception as e:
            print(metric + " failed forecast")
    full_df.to_csv("full_df_before_retunr.csv")
    return full_df

def forecast_model_selection(metric_df_trimmed,test_periods,forecast_periods,sp=None,tweeks=5):
    if tweeks == 'nope':
        tweeks = 5
    #sp = 52  
    #Split between the training and the test data sets. The last 12 periods form the test data.
    #test_periods = 12
    #forecast_periods = 12
    df_train = metric_df_trimmed.iloc[:-test_periods]
    freq = metric_df_trimmed.index.freq.name
    df_test = metric_df_trimmed.iloc[-test_periods:]
    df_test.index.freq=freq
    df_name = metric_df_trimmed.name
    
    model_json = [
    {"model_type":"hw","model_name":"hw_no_fit","model":"HWES(df_train)"},
    {"model_type":"hw","model_name":"hw_seasonal", "model":"HWES(df_train, seasonal_periods=sp)"},
    {"model_type":"hw","model_name":"hw_seasonal_trend-add_seasonal-add","model":"HWES(df_train, seasonal_periods=sp,trend='add',seasonal='add')"},
    {"model_type":"hw","model_name":"hw_seasonal_trend-mul_seasonal-add","model":"HWES(df_train, seasonal_periods=sp,trend='mul',seasonal='add')"},
    {"model_type":"hw","model_name":"hw_seasonal_trend-mul_seasonal-mul","model":"HWES(df_train, seasonal_periods=sp,trend='mul',seasonal='mul')"},
    {"model_type":"hw","model_name":"hw_seasonal_trend-add_seasonal-mul","model":"HWES(df_train, seasonal_periods=sp,trend='add',seasonal='mul')"},
    {"model_type":"average","model_name":"simple_trailing_average","model":{"weeks":tweeks}},
    
    ]

    selected_Rsquared = 'not set'
    mI = 0
    for m in model_json:
        try:
            forecast_column = df_name + '_forecast_value'
            model_type = m['model_type']
            model_name = m['model_name']
            print ("trying " + model_name + "...")
            model_string = m['model']
            if model_type == 'hw':
                model = eval(model_string)
                #model = HWES(df_train, seasonal_periods=52)
                fitted = None
                fitted = model.fit()
                
                #Create an out of sample forecast for the next 12 steps beyond the final data point in the training data set.
                test_forecast = fitted.forecast(steps=forecast_periods + test_periods)
                test_forecast = pd.Series.to_frame(test_forecast)
                forecast_column = df_name + '_forecast_value'
                test_forecast.columns = [forecast_column]
                
            if model_type == 'average':
                #print ("are we trying the average?")
                if model_name == 'simple_trailing_average':
                    model = 'simple_trailing_average'
                    weeks = model_string['weeks']
                    test_average = df_test[-weeks:].mean()
                    forecast_start_date = df_test.index.min()
                    forecast_index = pd.date_range(forecast_start_date,periods = test_periods+forecast_periods,freq=freq)
                    #print("forecast_index...")
                    #print(forecast_index)
                    test_forecast = forecast_index.to_frame()
                    test_forecast[forecast_column] = test_average
                    test_forecast = test_forecast.drop(0,axis=1)
                    
            test_comp_df = pd.merge(df_test,test_forecast,how='outer',left_index=True,right_index=True)     
                
            
            test_comp_df['Rsquared'] = (test_comp_df[df_name] - test_comp_df[forecast_column])**2
            Rsquared = test_comp_df.Rsquared.sum()
            if Rsquared == 0:
                #failsafe for models that throw null values
                1/0
            #print ("model" + str(mI) + " Rsquared = " + str(Rsquared))
            #print(test_comp_df)
            #print(fitted.summary())
            if selected_Rsquared == 'not set':
                selected_Rsquared = Rsquared
                selected_model_name = model_name
                selected_model = model
                selected_output = test_comp_df
                selected_output = selected_output.drop([df_name,'Rsquared'],axis=1)
                selected_output[df_name + '_forecast_model'] = model_name
                selected_model_json = model_json[mI]
            
            else:
                if Rsquared < selected_Rsquared:
                    selected_Rsquared = Rsquared
                    selected_model_name = model_name
                    selected_model = model
                    selected_output = test_comp_df
                    selected_output = selected_output.drop([df_name,'Rsquared'],axis=1)
                    selected_output[df_name + '_forecast_model'] = model_name
                    selected_model_json = model_json[mI]
                    
            
        except Exception as e:
            print (model_name + " failed")
        mI = mI + 1
            #print (str(e))
    print ("selected model = " + selected_model_name)
    #print (selected_output)
    selected_model_json['output_df'] = selected_output
    
    
    return selected_model_json
    #use the selected model to forecast the next periods

def find_forecast_start(metric_df,tperiods=9,stdevcount=1):
    start_date_list = []
    average = metric_df.tail(tperiods).mean()   
    stdev = metric_df.tail(tperiods).std()
    threshold = average - stdev*stdevcount
    min_periods_above_threshold = tperiods-1
    #start the df where n-1 forward looking periods are above the threshold, and the individual point is above the threshold
    mdI = 0
    for value in metric_df:
        row_start = mdI
        row_end = mdI + tperiods
        subdf = metric_df[row_start:row_end]
        avg = subdf.mean()
        count = len(subdf[subdf >= threshold])
        if avg >= threshold and count >= min_periods_above_threshold:
            start_date = metric_df.index[mdI]
            start_date_list.append(start_date)
        mdI = mdI + 1
    
    if len(start_date_list) == 0:
        forecast_start_date = metric_df.index[0]
    else:
        forecast_start_date = start_date_list[0]
    trimmed_df = metric_df[metric_df.index >= forecast_start_date]
    if len(trimmed_df) < tperiods:
        trimmed_df = metric_df.tail(tperiods)
    
    return trimmed_df
# forecast_metrics_list = ['users_created_per_day','users_closed_per_day','close_rate']
# sot_forecast_df = add_forecast_to_df(new_users_weekly,forecast_metrics_list,test_periods,forecast_periods,sp=52,freq='W-Sun')
# print(sot_forecast_df)
# sot_forecast_df.to_csv("sot_forecast.csv")