#!/usr/bin/python3

# Capture a JPEG using the still mode

import cv2

from picamera2 import Picamera2

picam2 = Picamera2()

# - Selected unicam format: 4656x3496-pRAA
preview_config = picam2.create_still_configuration(main = {"size": (4656, 3496), "format": "BGR888"})
picam2.configure(preview_config)

picam2.start()

# capture main.
np_array = picam2.capture_array()
# convert to cv2 internal format.
rgb = cv2.cvtColor(np_array, cv2.COLOR_BGRA2RGB)
cv2.imwrite("/tmp/now.jpg", rgb)

picam2.close()
