#!/usr/bin/python3

import RPi.GPIO as GPIO
import sys
import time

class JFCBot(object):
	
	def __init__(self,ain1=21,ain2=20,ena=16,bin1=19,bin2=26,enb=13):
		self.AIN1 = ain1
		self.AIN2 = ain2
		self.BIN1 = bin1
		self.BIN2 = bin2
		self.ENA = ena
		self.ENB = enb

		GPIO.setmode(GPIO.BCM)
		GPIO.setwarnings(False)
		GPIO.setup(self.AIN1,GPIO.OUT)
		GPIO.setup(self.AIN2,GPIO.OUT)
		GPIO.setup(self.BIN1,GPIO.OUT)
		GPIO.setup(self.BIN2,GPIO.OUT)
		GPIO.setup(self.ENA,GPIO.OUT)
		GPIO.setup(self.ENB,GPIO.OUT)
		self.stop()

	def backward(self):
		GPIO.output(self.AIN1,GPIO.HIGH)
		GPIO.output(self.AIN2,GPIO.HIGH)
		GPIO.output(self.BIN1,GPIO.HIGH)
		GPIO.output(self.BIN2,GPIO.HIGH)
		GPIO.output(self.ENA,GPIO.HIGH)
		GPIO.output(self.ENB,GPIO.HIGH)

	def stop(self):
		GPIO.output(self.AIN1,GPIO.LOW)
		GPIO.output(self.AIN2,GPIO.LOW)
		GPIO.output(self.BIN1,GPIO.LOW)
		GPIO.output(self.BIN2,GPIO.LOW)
		GPIO.output(self.ENA,GPIO.LOW)
		GPIO.output(self.ENB,GPIO.LOW)

	def forward(self):
		GPIO.output(self.AIN1,GPIO.LOW)
		GPIO.output(self.AIN2,GPIO.LOW)
		GPIO.output(self.BIN1,GPIO.LOW)
		GPIO.output(self.BIN2,GPIO.LOW)
		GPIO.output(self.ENA,GPIO.HIGH)
		GPIO.output(self.ENB,GPIO.HIGH)


		
	def right(self):
		GPIO.output(self.AIN1,GPIO.HIGH)
		GPIO.output(self.AIN2,GPIO.HIGH)
		GPIO.output(self.BIN1,GPIO.LOW)
		GPIO.output(self.BIN2,GPIO.LOW)
		GPIO.output(self.ENA,GPIO.HIGH)
		GPIO.output(self.ENB,GPIO.HIGH)


	def left(self):
		GPIO.output(self.AIN1,GPIO.LOW)
		GPIO.output(self.AIN2,GPIO.LOW)
		GPIO.output(self.BIN1,GPIO.HIGH)
		GPIO.output(self.BIN2,GPIO.HIGH)
		GPIO.output(self.ENA,GPIO.HIGH)
		GPIO.output(self.ENB,GPIO.HIGH)
		
if __name__=='__main__':

	Ab = JFCBot()
	if len(sys.argv) == 2:
		if sys.argv[1] == "Left":
			Ab.left()
			time.sleep(0.05)
		if sys.argv[1] == "Right":
			Ab.right()
			time.sleep(0.05)
		if sys.argv[1] == "Forward":
			Ab.forward()
			time.sleep(0.5)
		if sys.argv[1] == "Backward":
			Ab.backward()
			time.sleep(0.5)
	GPIO.cleanup()
