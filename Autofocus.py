#!/usr/bin/python3
# Try to autofocus the Arducam 64MP camera

import cv2
#import numpy as py
import os
from picamera2 import Picamera2
import time
import v4l2
import fcntl
import errno
# JFC import smbus
# JFC bus = smbus.SMBus(0)

fd = open("/dev/v4l-subdev1", 'r')
FOCUS_ID = 0x009a090a

def set_ctrl(vd, id, value):
    ctrl = v4l2.v4l2_control()
    ctrl.id = id
    ctrl.value = value
    try:
        fcntl.ioctl(vd, v4l2.VIDIOC_S_CTRL, ctrl)
    except IOError as e:
        print(e)
	
def focusingi2c(val):
	value = (val << 4) & 0x3ff0
	data1 = (value >> 8) & 0x3f
	data2 = value & 0xf0
	# time.sleep(0.5)
	print("focus value: {}".format(val))
        # bus.write_byte_data(0x0c,data1,data2)
	print("i2cset -y 22 0x0c %d %d" % (data1,data2))
	os.system("i2cset -y 22 0x0c %d %d" % (data1,data2))
def focusing(val):
	print("focus value: {}".format(val))
	set_ctrl(fd, FOCUS_ID, val)	
	
def sobel(img):
	img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	img_sobel = cv2.Sobel(img_gray,cv2.CV_16U,1,1)
	return cv2.mean(img_sobel)[0]

def laplacian(img):
	img_gray = cv2.cvtColor(img,cv2.COLOR_RGB2GRAY)
	img_sobel = cv2.Laplacian(img_gray,cv2.CV_16U)
	return cv2.mean(img_sobel)[0]
	

def calculation(camera):
	image = cam.capture_array()
# JFC	ret , image = cam.read()
	return laplacian(image)
	
	
if __name__ == "__main__":
    #open camera

	# video = open("/dev/video0",'rb') 
	# framesize = 4656 * 3496
	# initbyte = framesize * initframe
	# initbyte = framesize * 1
	# video.seek(initbyte)
	# frame = video.read(framesize)
	# frame = np.frombuffer(frame, dtype=np.uint8).reshape(600,1920)
	cam = Picamera2()
	config = cam.create_still_configuration()
	cam.configure(config)
	cam.start()
	image = cam.capture_array()
	image = cam.capture_array()
# JFC	print(np_array)
# JFC	cam.capture_file("demo.jpg")
# JFC	cam.stop()

# JFC	cam = cv2.VideoCapture(0)
# JFC	if cam.isOpened():
# JFC		print("Cam OK!")
# JFC	else:
# JFC		print("Cam FAILED!")
# JFC	# wrong width or height 640x480 (remote pad set to 4656x3496)
# JFC	cam.set(cv2.CAP_PROP_FRAME_WIDTH,4656)
# JFC	cam.set(cv2.CAP_PROP_FRAME_HEIGHT,3496)
# JFC	# some thing else from libcamera-hello --verbose
# JFC	# INFO RPI raspberrypi.cpp:759 Sensor: /base/soc/i2c0mux/i2c@1/imx519@1a - Selected sensor format: 2328x1748-SRGGB10_1X10 - Selected unicam format: 2328x1748-pRAA
# JFC	#cam.set(cv2.CAP_PROP_FRAME_WIDTH,2328)
# JFC	#cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1748)
# JFC	cam.set(cv2.CAP_PROP_CONVERT_RGB, 0)
# JFC	#cam.set(cv2.CAP_PROP_MODE, -1)
# JFC	ret = cam.grab()
# JFC	print("grab() Ret: ", ret) 
# JFC	ret = cam.grab()
# JFC	print("grab() Ret: ", ret) 
# JFC	time.sleep(0.1)
# JFC	ret , image = cam.read()
# JFC	print("Ret: ", ret) 
# JFC	ret , image = cam.read()
# JFC	print("Ret: ", ret) 
	cv2.imwrite('/tmp/unfocusedImage.jpg', image)
	print("Start focusing")
	
	max_index = 10
	max_value = 0.0
	last_value = 0.0
	dec_count = 0
	# focal_distance = 10
	focal_distance = 800


        

	while True:
	    #Adjust focus
		focusing(focal_distance)
		#Take image and calculate image clarity
		val = calculation(cam)
		#Find the maximum image clarity
		if val > max_value:
			max_index = focal_distance
			max_value = val
			
		#If the image clarity starts to decrease
		if val < last_value:
			dec_count += 1
		else:
			dec_count = 0
		#Image clarity is reduced by six consecutive frames
		if dec_count > 6:
			break
		last_value = val
		
		#Increase the focal distance
		focal_distance += 15
		if focal_distance > 1000:
			break

    #Adjust focus to the best
	focusing(max_index)
	time.sleep(1)
	image = cam.capture_array()
#JFC 	ret , image = cam.read()
	cv2.imwrite('/tmp/focusedImage.jpg', image)
	cam.stop()
