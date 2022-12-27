#!/usr/bin/python3
# motor driver drv8830 version

from drv8830 import DRV8830, I2C_ADDR1, I2C_ADDR2
import sys
import time

class JFCBot(object):
	
	def __init__(self):
		self.left = DRV8830(I2C_ADDR1)
		self.right = DRV8830(I2C_ADDR2)


	def backward(self):
		self.left.set_voltage(5)
		self.right.set_voltage(5)
		self.left.reverse()
		self.right.reverse()

	def stop(self):
		self.left.set_voltage(5)
		self.right.set_voltage(5)
		self.left.coast()
		self.right.coast()

	def forward(self):
		self.left.set_voltage(5)
		self.right.set_voltage(5)
		self.left.forward()
		self.right.forward()
		
	def Myright(self):
		self.left.set_voltage(2.5)
		self.right.set_voltage(2.5)
		self.left.forward()
		self.right.reverse()

	def Myleft(self):
		self.left.set_voltage(2.5)
		self.right.set_voltage(2.5)
		self.left.reverse()
		self.right.forward()

	def stop(self):
		self.left.set_voltage(0)
		self.right.set_voltage(0)

		
if __name__=='__main__':

	Ab = JFCBot()
	if len(sys.argv) == 2:
		if sys.argv[1] == "Left":
			Ab.Myleft()
			time.sleep(0.5)
		if sys.argv[1] == "Right":
			Ab.Myright()
			time.sleep(0.5)
		if sys.argv[1] == "Forward":
			Ab.forward()
			time.sleep(0.5)
		if sys.argv[1] == "Backward":
			Ab.backward()
			time.sleep(0.5)
	Ab.stop()
