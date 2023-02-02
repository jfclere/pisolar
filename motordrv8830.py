#!/usr/bin/python3
# motor driver drv8830 version

from drv8830 import DRV8830, I2C_ADDR1, I2C_ADDR2
import sys
import time

class JFCBot(object):
	
	def __init__(self):
		self.left = DRV8830(I2C_ADDR1)
		self.right = DRV8830(I2C_ADDR2)


	def forward(self):
		self.left.set_voltage(3)
		self.right.set_voltage(3)
		self.left.forward()
		self.right.reverse()

	def stop(self):
		self.left.set_voltage(5)
		self.right.set_voltage(5)
		self.left.coast()
		self.right.coast()

	def backward(self):
		self.left.set_voltage(3)
		self.right.set_voltage(3)
		self.left.reverse()
		self.right.forward()
		
	def Myleft(self):
		self.left.set_voltage(3)
		self.right.set_voltage(3)
		self.left.reverse()
		self.right.reverse()

	def Myright(self):
		self.left.set_voltage(3)
		self.right.set_voltage(3)
		self.left.forward()
		self.right.forward()

	def stop(self):
		self.left.set_voltage(0)
		self.right.set_voltage(0)

	def status(self):
                left = self.left.get_fault().fault
                right = self.right.get_fault().fault
                return left, right
		
	def debugstatus(self):
		left = self.left.get_fault()
		right = self.right.get_fault()
		return(left, right)

if __name__=='__main__':

	Ab = JFCBot()
	if len(sys.argv) == 2:
		if sys.argv[1] == "Left":
			Ab.Myleft()
			time.sleep(0.1)
		elif sys.argv[1] == "Left90":
			Ab.Myleft()
			time.sleep(0.42)
		elif sys.argv[1] == "Right":
			Ab.Myright()
			time.sleep(0.1)
		elif sys.argv[1] == "Right90":
			Ab.Myright()
			time.sleep(0.42)
		elif sys.argv[1] == "Forward":
			Ab.forward()
			time.sleep(0.5)
		elif sys.argv[1] == "Backward":
			Ab.backward()
			time.sleep(0.5)
		elif sys.argv[1] == "Status":
			status = Ab.status()
			if status[0] == 1 or status[1] == 1:
				print("Failed!")
		else:
			print("Status: ",Ab.debugstatus())
	Ab.stop()
