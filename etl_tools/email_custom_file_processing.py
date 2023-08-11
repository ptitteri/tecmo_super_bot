# -*- coding: utf-8 -*-
"""
Created on Fri Mar 26 17:17:02 2021
@author: peter.titterington

Updated on Thu Apr 8 2021
@coauthor: gavin.cleveland
added additional functionality to format the file
"""

import datetime
import pandas as pd
pd.options.mode.chained_assignment = None

def sage_mec(df):
    mec_date = df['Closing balance'].to_list()[0]
    mec_date = datetime.datetime.strptime(mec_date,'%m/%d/%Y')
    location_list = df[df.index==0].values.tolist()[0]
    header_rename_list = df.columns.tolist()

    # create dictionary of column values
    cols_rename_dict = {i:j for i,j in zip(header_rename_list,location_list)}

    # update value for closing balance key
    cols_rename_dict['Closing balance'] = 'Closing balance'

    # condense df to exclude first header row
    adj_df = df[1:]
    adj_df.rename(columns= cols_rename_dict, inplace=True)

    # drop totals row from df
    df_trunc = adj_df[~adj_df.Number.str.contains('Totals')]

    # assign month end date
    df_trunc['month_end_date'] = mec_date

    # filter df to set columns
    df_trun = df_trunc[['Number','Name','month_end_date', 'Closing balance']]
    df_trun.columns=['account_number','account_name','month_ending_date', 'closing_balance']
    return df_trun
