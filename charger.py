#!/usr/bin/python3
# wait until charged...
# 550 = low value

import RPi.GPIO as GPIO
import os
import time
import socket
import sys
import traceback
import psutil
import wifi

from nodeinfo import nodeinfo
from readreg import readreg
from writereg import writereg
from reportserver import reportserver

CHARGEGPIO=26

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
GPIO.setup(CHARGEGPIO,GPIO.IN)

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

if not net:
  print("NO Network!")

myinfo = nodeinfo()
if myinfo.read():
  # Use some default values
  print("myinfo.read() Failed!");
  myinfo.TIME_ACTIVE = 0
  myinfo.WAIT_TIME = 120
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

# send our IP to the server
if net:
  try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    val = s.getsockname()[0]
    s.close()
    mess = "IP :  " + str(val)
    mess = bytes(mess, 'utf-8')
    url = "/webdav/" + myinfo.REMOTE_DIR + "/ip.txt"
    mywifi = wifi.wifi()
    mywifi.sendserver(mess, url, myinfo.machine, 443, myinfo.login, myinfo.password)
  except Exception as ex:
    print("Send IP to web failed")
    print(str(ex))
    traceback.print_exception(type(ex), ex, ex.__traceback__)

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

# check if we are charging...
i = GPIO.input(CHARGEGPIO)
if i:
  print("charging and " + str(myinfo.TIME_ACTIVE))
  myreg = readreg()
  val = myreg.read(0)
  print("charging bat is: ", val)
  i=0
  for p in psutil.process_iter():
    if p.name() == 'sshd':
      print(p)
      i += 1
  if i >= 3:
    print("Don't kill!")
    exit()
  if val <= 550:
    # stop and wait
    stopatt(myinfo.WAIT_TIME)
  if myinfo.TIME_ACTIVE == 0:
    # stop and wait
    stopatt(myinfo.WAIT_TIME)

