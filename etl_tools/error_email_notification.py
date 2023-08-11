import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def email_composition(sender,recipients,subject,body):
    try:
        ses = boto3.client("ses","us-east-2")
        #email body and attachments
        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"]= sender
        msg["To"] = ', '.join(recipients)
        body_txt = MIMEText(body,"html")
        msg.attach(body_txt)
        response = ses.send_raw_email(Source=sender, Destinations=recipients, RawMessage={"Data":msg.as_string()})
        print("error message emailed successfully")
    except Exception as e:
        print(e)


def sot_bot_notification(job_type="No value",reference_link="No value",job_start_datetime="No value",message="No value"):
    message = str(message).replace('<','').replace('>','')
    if job_type.find("etl_jobs") != -1:
        job_type = 'ETL'
    elif job_type == "email_jobs":
        job_type = 'EMAIL'
    elif job_type == "model_runs":
        job_type = 'MODEL'

    sender = "sot_bot@pillpack.com <kiran.kadlag@pillpack.com>"
    #sender = "sot_bot@pillpack.com <peter.titterington@pillpack.com>"
    recipients = ["kiran.kadlag@pillpack.com"]
    subject = "SOT_BOT Error Notification"
    body = """
            Hello,
            <br><br>This message was created automatically by SOT bot.
            <br>There is an error in executing following code.
            <br><br>Job Type : {job_type}
            <br>Code : {code_link}
            <br>Start time : {job_start_datetime}
            <br>Error Message : {message}
            <br><br>
            -- SOT bot
    """.format(job_type=job_type,code_link=reference_link,job_start_datetime=job_start_datetime,message=message)
    email_composition(sender,recipients,subject,body)
