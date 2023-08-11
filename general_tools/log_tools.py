# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:25:14 2022

@author: ptitt
"""


def write_to_log(file_name,lines,mode):
    #mode 'a' = append, 'w' = write new
    with open(file_name + '.txt', mode) as f:
        for line in lines:
            f.write('\n'.join(lines))
            f.write('\n')

import csv
def write_to_csv(field_names,log_data, csv_file_path,write_mode):
    with open(csv_file_path, write_mode, newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=field_names)
        if write_mode == 'w':
            writer.writeheader()
        writer.writerows(log_data)
        
