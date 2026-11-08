#!/usr/bin/python3
# The PIR is on GPIO4
from picamzero import Camera
import os
import RPi.GPIO as GPIO
from nodeinfo import nodeinfo
import wifi
import datetime

VAL = 18

count = 0
def callback():
   global count
   count = count + 1

def isalarm():
   global count
   if count >= 2:
     print(count)
     count = 0
     print(count)
     return True
   else:
     count = 0
     return False

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 4
GPIO.setup(PIR_PIN, GPIO.IN)

cam = Camera()

myinfo = nodeinfo()
myinfo.read()
mywifi = wifi.wifi()

timecount = 0
while True:
  myalarm = False
  if GPIO.input(PIR_PIN):
    callback()
  if timecount == VAL and isalarm():
    myalarm = True
  if myalarm:
    cam.take_photo("/tmp/current.jpg")
    f = open("/tmp/current.jpg", 'rb')
    mess = f.read()
    f.close()
    d = datetime.datetime.now()
    url = "/webdav/" + myinfo.REMOTE_DIR + "/" + d.strftime("%Y%m%d")
    mywifi.createdirserver(url, myinfo.machine, 443, myinfo.login, myinfo.password) 
    url = "/webdav/" + myinfo.REMOTE_DIR + "/" + d.strftime("%Y%m%d") + "/" + d.strftime("%H") + "00"
    mywifi.createdirserver(url, myinfo.machine, 443, myinfo.login, myinfo.password) 
    url = "/webdav/" + myinfo.REMOTE_DIR + "/" + d.strftime("%Y%m%d") + "/" + d.strftime("%H") + "00" + "/" + d.strftime("%Y%m%d%H%M%S") + ".jpg"
    mywifi.sendserver(mess, url, myinfo.machine, 443, myinfo.login, myinfo.password)
  if timecount >= VAL:
    timecount = 0
  else:
    timecount = timecount + 1
