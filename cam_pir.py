#!/usr/bin/python3
# The PIR is on GPIO4
from picamzero import Camera
import os
import RPi.GPIO as GPIO
from nodeinfo import nodeinfo
import wifi
import datetime

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
PIR_PIN = 4
GPIO.setup(PIR_PIN, GPIO.IN)

cam = Camera()

myinfo = nodeinfo()
myinfo.read()
mywifi = wifi.wifi()

while True:
  if GPIO.input(PIR_PIN):
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
