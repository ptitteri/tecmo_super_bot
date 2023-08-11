import pandas as pd
import datetime
from aws_tools.console_tools import push_df_to_s3,get_s3_csv_dataframe


def bot_run_logs(job_type="No value", reference_link="No value", job_start_datetime="No Value", error_message="No value"):

    job_end_datetime = str(datetime.datetime.now())[:16]
    aws_bucket = 'pillpack-sot-metadata'
    aws_path = 'bot_run_logs/'
    aws_file = job_end_datetime[:7] + '_bot_run_logs.csv'
    try:
        df = get_s3_csv_dataframe(aws_bucket, aws_path+aws_file)
    except:
        df = pd.DataFrame(columns=['job_type', 'reference_link', 'start_time', 'end_time', 'error'])
        push_df_to_s3(df, aws_bucket, aws_path, aws_file, file_type="csv", include_header=True)

    try:
        if job_type.find("etl_jobs") != -1:
            job_type = 'etl'
        elif job_type == "email_jobs":
            job_type = 'email'
        elif job_type == "model_runs":
            job_type = 'model'

        logs = {'job_type': [job_type],
                'reference_link': [reference_link],
                'start_time': [job_start_datetime],
                'end_time': [job_end_datetime],
                'error': [error_message]}
        logs = pd.DataFrame(logs)
        df = df.append(logs)
        push_df_to_s3(df, aws_bucket, aws_path, aws_file, file_type="csv", include_header=True)
        print("logs updated successfully")
    except Exception as e:
        print(e)
