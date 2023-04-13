import sys
import os 
from Pan_Extraction import *
from PIL import Image
import io

# Update your AWS Reckognition credentials 
getClass = Pan_Extraction(aws_key='',aws_secret='')

# Set image path
im = Image.open("pancard_sample.jpg")

# Convert image into bytes
img_byte_arr = io.BytesIO()
im.save(img_byte_arr, format='PNG')
img_byte_arr = img_byte_arr.getvalue()

print(getClass.parsePanFront(img_byte_arr))
