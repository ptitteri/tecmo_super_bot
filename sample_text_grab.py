# -*- coding: utf-8 -*-
"""
Created on Sun Aug  1 15:11:54 2021

@author: ptitt
"""


# Import required packages
import cv2
import pytesseract
  
# Mention the installed location of Tesseract-OCR in your system
#pytesseract.pytesseract.tesseract_cmd = 'System_path_to_tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = 'C:\\Users\\ptitt\\AppData\\Local\\Programs\\Tesseract-OCR\\tesseract.exe'
# Read image from which text needs to be extracted

  
# Preprocessing the image starts
  
# Convert the image to gray scale
def read_screen_text(processed_image):
    gray = processed_image #from screengrabs.py
      
    # Performing OTSU threshold
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)
      
    # Specify structure shape and kernel size. 
    # Kernel size increases or decreases the area 
    # of the rectangle to be detected.
    # A smaller value like (10, 10) will detect 
    # each word instead of a sentence.
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (18, 18))
      
    # Appplying dilation on the threshold image
    dilation = cv2.dilate(thresh1, rect_kernel, iterations = 1)
      
    # Finding contours
    contours, hierarchy = cv2.findContours(dilation, cv2.RETR_EXTERNAL, 
                                                     cv2.CHAIN_APPROX_NONE)
      
    # Creating a copy of image
    im2 = processed_image
      
      
    # Looping through the identified contours
    # Then rectangular part is cropped and passed on
    # to pytesseract for extracting text from it
    # Extracted text is then written into the text file
    text_found = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
          
        # Drawing a rectangle on copied image
        rect = cv2.rectangle(im2, (x, y), (x + w, y + h), (0, 255, 0), 2)
          
        # Cropping the text block for giving input to OCR
        cropped = im2[y:y + h, x:x + w]
        # Apply OCR on the cropped image
        text = pytesseract.image_to_string(cropped)
        text_found.append(text)
        print(text)
          
        # # # Appending the text into file
        file = open("recognized.txt", "w+")
        file.write(text)
        file.write("\n")
        file.close()
    return text_found
