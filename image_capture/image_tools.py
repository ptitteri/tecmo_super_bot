# -*- coding: utf-8 -*-
"""
Created on Thu Nov  3 09:30:56 2022

@author: ptitt
"""
import cv2
import pytesseract
import numpy as np
from window_manager import WindowMgr
from PIL import ImageGrab
import boto3
path_to_tesseract = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
#Point tessaract_cmd to tessaract.exe
pytesseract.tesseract_cmd = path_to_tesseract

#process image in various ways, kind of a placeholder right now
def process_image(original_image):
    #color
    #processed_image = cv2.cvtColor(original_image,cv2.COLOR_BGR2RGB)

    #B/W only
    processed_image = cv2.cvtColor(original_image,cv2.COLOR_BGR2GRAY)
    #lines only
    #processed_image = cv2.Canny(original_image,threshold1=200,threshold2=300)
    #parse out text from image
    #text = read_screen_text(processed_image)
    return processed_image
    #return original_image

#simple text extraction from image. psms can be tuned for different images
def extract_text_from_image(image,psm=3):
    #configure for best results
    config_str = ('-l eng --oem 1 --psm '+str(psm))
    #print (config_str)
    extracted_text = pytesseract.image_to_string(
            image,
            config=config_str
        )
    #print(extracted_text)
    return extracted_text


#returns image based on keyword  search
def find_window_image(window_type):
    w = WindowMgr()
    w.find_window_wildcard(".*"+window_type+"*")
    w.dimensions()
    image = np.array(ImageGrab.grab(bbox=w._dims))
    return image


def textract_input(local_image):
    textract = boto3.client('textract','us-west-2')
    with open(local_image, 'rb') as image_file:
        image_bytes = image_file.read()

    response = textract.detect_document_text(Document={'Bytes': image_bytes})
    return response

def textract_response(screenshot,image_local_file_path = r'C:/users/ptitt/desktop/textract_image.jpg'):
    cv2.imwrite(image_local_file_path,screenshot)
    response = textract_input(image_local_file_path)
    return response

response = textract_response(screenshot,image_local_file_path)