# -*- coding: utf-8 -*-
"""
Created on Sun May 28 09:58:40 2023

@author: ptitt
"""

#Initialize a client for Amazon Textract
textract = boto3.client('textract','us-west-2')

# Specify the S3 bucket and key where the image is stored
bucket_name = aws_bucket
image_key = aws_path + aws_file

with open(image_local_file_path, 'rb') as image_file:
    image_bytes = image_file.read()

response = textract.detect_document_text(Document={'Bytes': image_bytes})

# response = textract.detect_document_text(
#     Document={
#         'S3Object': {
#             'Bucket': bucket_name,
#             'Name': image_key
#         }
#     })

# Print detected text
next_block = 'keep moving'
for item in response["Blocks"]:
    if item["BlockType"] == "LINE":
      text = (item["Text"] + '\n')
      print(text)      
      if next_block == 'down':
          down = text
      elif next_block == 'yardline':
          yardline = text
      elif next_block == 'posession':
          posession = text
      elif next_block == 'ytg':
          ytg = text
      else:
          do_nothing = 1
     #key off the order of the blocks. the preceding block tells you the content of the next one
      if text == 'DOWN:':
          next_block = 'down'
      elif text == 'YARDLINE:':
          next_block = 'yardline'
      elif text.find('POSESSION')!= -1:
          next_block = 'posession'
      elif text.find('YARDS TO GO')!= -1:
          next_block = 'ytg'
      else:
          next_block = 'keep moving'
      
      
      
if posession.find('1') !=-1:
    ball = 'away'
elif posession.find('1') == -1:
    ball = 'home'
else:
    ball = 'unknown'
    
    
situation_json = {"down":int(down)
                ,"yardline":int(yardline)
                ,"yards_to_go":int(ytg)
                ,"posession":ball
                
                    }    
print (situation_json)