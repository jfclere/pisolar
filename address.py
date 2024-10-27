#!/usr/bin/python3
# Send the address to the server.
# 550 = low value

import RPi.GPIO as GPIO
import os
import time
import socket
import sys
import traceback
import wifi

from nodeinfo import nodeinfo
from reportserver import reportserver

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
