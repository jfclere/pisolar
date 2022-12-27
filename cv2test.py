#!/usr/bin/python3
# just filter image for red colors

import cv2
import numpy as np
from pyzbar import pyzbar

cam = cv2.VideoCapture(0)
 
#image = cv2.imread('dd9tg.jpg')
ret , image = cam.read()
#cv2.imshow("Original", image)
cv2.imwrite('origImage.jpg',image)
 
result = image.copy()
 
result = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)
result = cv2.GaussianBlur(result, (3, 3), 0)
barcodes = pyzbar.decode(result)
if barcodes is None:
   print("Not found")
else:
   (x, y, w, h) = barcode.rect
   qx=x+round(w/2)
   qy=y+round(h/2)
   cv2.rectangle(result, (x, y), (x + w, y + h), (0, 0, 255), 2)
   cv2.rectangle(result, (qx-5, qy-5), (qx+5, qy+5), (0, 255, 0), 2)
   barcodeData = barcode.data.decode("utf-8")
   barcodeType = barcode.type
   text = "{} ({})".format(barcodeData, barcodeType)
   cv2.putText(result, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,0.5, (0, 0, 255), 2)

cv2.imwrite('processedImage.jpg.jpg', result)

cam.release()
