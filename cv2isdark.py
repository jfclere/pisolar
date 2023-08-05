#!/usr/bin/python3
# Check if the picture is dark (night for example).
#

import cv2
import numpy

# open the file with opencv
image = cv2.imread("/tmp/now.jpg", cv2.IMREAD_GRAYSCALE)
if image is None:
    exit(1)
num = numpy.mean(image) * 100 / 255
print("cv2.countNonZero image: " + str(num))
if num <= 1:
    print("Image is black")
    exit(0)
else:
    print("Colored image")
    exit(1)
