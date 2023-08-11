# -*- coding: utf-8 -*-
"""
Created on Wed May 19 16:37:34 2021

@author: peter.titterington
"""


from google_tools.google_api import pull_gsheet_data
import os

input_folder = 'C://Users//peter.titterington//Documents//replica_project//file_inputs//'
output_folder = 'C://Users//peter.titterington//Documents//replica_project//file_outputs//'

file_list = os.listdir(input_folder)
        

#1 import the list of items to swap
swap_workbook_id = '1Pl8Ye9BxUUHRK8RBYCY4gID59r-ROUBYWgEvFXCfFDc'
range_name = 'search_and_replace!A1:C'
swap_df = pull_gsheet_data(swap_workbook_id,range_name)

for f in file_list:
    #2 import the yaml file
    f = f.replace(".yaml","")
    yaml_file = open(input_folder + f + '.yaml')
    yaml_data = yaml_file.read()
    
    rI = 0
    for r in swap_df['prod_replica_term']:
        search = swap_df['prod_replica_term'][rI]
        replace = swap_df['looker_production_term'][rI]
        yaml_data = yaml_data.replace(search,replace)
        rI = rI + 1
    with open(output_folder + f +"_converted.yaml", 'w') as file:
      file.write(yaml_data)
        
    
