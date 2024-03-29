#!/usr/bin/python3
# ocean 5V on gpio=23

import RPi.GPIO as GPIO
import os
import time
import socket
from nodeinfo import nodeinfo
from readreg import readreg
from writereg import writereg
from reportserver import reportserver

OCEANGPIO=23
BLUELED=26

# update register of the ATtiny
def updatereg(nodeinfo, readreg):
  batlow = readreg.read(2)
  batcharged = readreg.read(4)
  setbatlow = nodeinfo.BAT_LOW
  setbatcharged = nodeinfo.BATCHARGED
  if setbatlow > 0 and setbatlow != batlow:
    print("batlow: " + str(batlow) + ":" + str(setbatlow))
    mywritereg = writereg()
    mywritereg.write(2, setbatlow)
  if setbatcharged > 0 and setbatcharged != batcharged:
    print("batcharged: " + str(batcharged) + ":" + str(setbatcharged))
    mywritereg = writereg()
    mywritereg.write(4, setbatcharged)

def stopatt(wait):
  mywritereg = writereg()
  mywritereg.write(8, wait)
  myreg = readreg()
  val = myreg.read(8)
  if val != wait:
    print("stopatt read doesn't give right value")
  os.system("sudo init 0")
    

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(OCEANGPIO,GPIO.OUT)
GPIO.output(OCEANGPIO,GPIO.LOW)

# wait until we have an IP
i = 1
while i < 30:
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
  except: 
    time.sleep(1)
    i += 1
    continue
  break
net = True 
if i == 30:
  # We don't have network
  net = False
  GPIO.setup(BLUELED,GPIO.OUT)
  GPIO.output(BLUELED,GPIO.HIGH)

if not net:
  print("NO Network!")

myinfo = nodeinfo()
if myinfo.read():
  # Use some default values
  print("myinfo.read() Failed!");
  myinfo.TIME_ACTIVE = 1
  myinfo.WAIT_TIME = 3405
  myinfo.MAINT_MODE = False

if myinfo.MAINT_MODE:
  # Maintenance mode required
  try:
    myreg = readreg()
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg)
  except: 
    print("report to server failed")
  print("myinfo.read() Failed maintenance mode!")
  exit()

if myinfo.TIME_ACTIVE > 0:
  GPIO.output(OCEANGPIO,GPIO.HIGH)
  print("on for " + str(myinfo.TIME_ACTIVE) + " Minutes")
  time.sleep(60*myinfo.TIME_ACTIVE)
  print("Done")

# end make sure to stop
GPIO.output(OCEANGPIO,GPIO.LOW)

# update register
if net:
  try:
    myreg = readreg()
    myreportserver = reportserver()
    myreportserver.report(myinfo, myreg)
    updatereg(myinfo, myreg)
  except: 
    print("report to server failed")
    net = False

# update software
if net:
  try:
    ver = myinfo.readsavedversion()
    if ver != myinfo.GIT_VER:
      cmd = "/home/pi/pisolar/gitver.sh " + myinfo.GIT_VER
      if os.system(cmd):
        print(cmd + " Failed")
      else:
        myinfo.saveconf()
  except: 
    print("software update failed")


# stop and wait
stopatt(myinfo.WAIT_TIME)
