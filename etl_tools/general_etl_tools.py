# -*- coding: utf-8 -*-





def body_range_calculator(header_range):
    colon = header_range.find(":")
    type_check = 'int'
    i = -1
    pete =0 
    while pete == 0:
        rownum = header_range[:colon][i:]
        try:
            int(row_num)
        except:
            pete=1
        i = i-1
    body_rownum = str(int(rownum)+1)
    body_range = header_range.replace(rownum,body_rownum)
    return body_range