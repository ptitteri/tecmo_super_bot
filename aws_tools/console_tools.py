# -*- coding: utf-8 -*-
"""
Created on Tue Sep  8 12:36:03 2020

@author: peter.titterington
"""
import boto3
import pandas as pd
import boto3
import botocore
import os
import datetime
import io



def push_local_file_to_s3(aws_bucket,aws_path,aws_file,local_file_path):
    s3_client = boto3.client('s3')
    try:
        s3_client.put_object(Bucket=aws_bucket, Key=(aws_path))
        print (aws_path + " created...")
    except:
        print (aws_path + " exists...")
    try:
        response = s3_client.upload_file(local_file_path, aws_bucket, aws_path+aws_file, ExtraArgs={'ACL':'bucket-owner-full-control'})
    except:
        print (local_file_path + " S3 publishing failed")
    return True

def push_df_to_s3(df,aws_bucket,aws_path,aws_file,file_type="csv",include_header=True):
    file_name = 'randomfile_' + str(datetime.datetime.now()).replace(":","-").replace(".","-").replace(" ","_")
    if file_type == "csv":
        df.to_csv(file_name,index=False,header=include_header)
    elif file_type == 'tsv':
        df.to_csv(file_name,index=False,sep='\t',header=include_header)
    elif file_type == 'gz':
        file_name = file_name + '.gz'
        df.to_csv(file_name, index=False, header=True, compression='gzip')
    try:
        push_local_file_to_s3(aws_bucket,aws_path,aws_file,file_name)
    except Exception as e:
        print (str(e))
    os.remove(file_name)
    

def pull_s3_file_to_df(aws_bucket,aws_path,aws_file,on_bad_lines=None, delimiter=None):
    s3_client = boto3.client('s3')
    try:
        file_name = "s3_temp_file_" + str(datetime.datetime.now()).replace(".","_").replace(":","-").replace(" ","_")
        s3_client.download_file(aws_bucket,aws_path+aws_file,file_name)
        df = pd.read_csv(file_name,on_bad_lines=on_bad_lines,delimiter=delimiter)
        #get the last modified time as well
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise Exception
    try:
        os.remove(file_name)
    except:
        print(file_name + " not present")
    return df

def s3_file_last_modified_datetime(aws_bucket,aws_path,aws_file):
    s3_client = boto3.client('s3')
    try:
        
        response = s3_client.head_object(Bucket = aws_bucket, Key=aws_path+aws_file)
        last_modified_datetime = response["LastModified"]
        
        bucket = s3_client.list_objects(Bucket = aws_bucket)
        # for b in bucket['Contents']:
        #     if b['Key'] == aws_path + aws_file:
        #         last_modified_datetime = b['LastModified']
        return last_modified_datetime
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise Exception
    
def get_s3_file_list(s3_bucket,s3_path=""):
    s3_client = boto3.client('s3')
    try:
        if s3_path == "":
            bucket = s3_client.list_objects(Bucket = s3_bucket)
        else:
            bucket = s3_client.list_objects(Bucket = s3_bucket,Prefix=s3_path)
        file_list = []
        for b in bucket['Contents']:
            if b['Key'].find(s3_path) != -1:
                file_list.append(b)
            
        return file_list
    except botocore.exceptions.ClientError as e:
        if e.response['Error']['Code'] == "404":
            print("The object does not exist.")
        else:
            raise Exception

def get_s3_csv_dataframe(s3_bucket,s3_read_path,skip_rows=0):
    s3_client = boto3.client('s3') 
    obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_read_path)
    df = pd.read_csv(io.BytesIO(obj['Body'].read()),skiprows=skip_rows)
    return df

def get_xl_from_s3(s3_bucket,s3_read_path):
    s3_client = boto3.client('s3')
    obj = s3_client.get_object(Bucket=s3_bucket, Key=s3_read_path)
    xl = pd.ExcelFile(io.BytesIO(obj['Body'].read()))
    return xl

def delete_s3_file(s3_bucket,s3_path):
    s3_client = boto3.client('s3')
    s3_client.delete_object(Bucket = s3_bucket,Key=s3_path)


