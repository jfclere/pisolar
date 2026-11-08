#!/usr/bin/python

import time
import math
import sys
import os
import AT_http_s

#
# This class read the info the server has for us
#
# REMOTE_DIR where to store the information in the server
# WAIT_TIME time to wait before restarting
# BAT_LOW low battery (won't start below the value)
# GIT_VER git version of the repo to use (auto update)
# BATCHARGED disconnect charging device once the battery reaches that value
# TIME_ACTIVE time the pump will run

class nodeinfo:
  REMOTE_DIR="pisolar"
  WAIT_TIME=500
  BAT_LOW=500
  GIT_VER="5fe4895"
  BATCHARGED=773
  TIME_ACTIVE=2
  MAINT_MODE=False
  ETAG=""

  # read the machine_id (/etc/machine-id)
  # read server info ($HOME/.netrc)
  def __init__(self):
    self.machine_id="a470a4070ed946d2ad6b98a9cf130f7b"
    try:
      text_file = open("/etc/machine-id");
      self.machine_id = text_file.readline().rstrip()
      text_file.close()
    except Exception as e:
      print('Exception: ' + str(e))

    self.server="jfclere.myddns.me"
    self.login="jfclere"
    self.password="changeit"
    home_directory = os.path.expanduser( '~' )
    try:
      text_file = open(home_directory + "/.netrc")
      for i in range(3): 
        txt = text_file.readline()
        x = txt.split(" ")
        if x[0] == "machine":
          self.machine=x[1].rstrip()
        if x[0] == "login":
          self.login=x[1].rstrip()
        if x[0] == "password":
          self.password=x[1].rstrip()
      text_file.close()
    except Exception as e:
      print('Exception: ' + str(e))
      return

  def fingerprint(self):
    return self.REMOTE_DIR + ":" + str(self.WAIT_TIME) + ":" + str(self.BAT_LOW) + ":" + self.GIT_VER + ":" + str(self.BATCHARGED) + ":" + str(self.TIME_ACTIVE)

  # get our configuration from server using SIM7028 AT commands
  def read(self):
    try:
      if not AT_http_s.HTTPINIT():
        return True
      if AT_http_s.HTTPPARA('https://' + self.server + '/machines/' + self.machine_id).PARA():
        AT_http_s.HTTPTERM()
        return True
      resp = AT_http_s.HTTPACTION(0)
      AT_http_s.HTTPTERM()
      if not resp:
        return True
      info = AT_http_s.decode_nodeinfo(resp)
      if 'REMOTE_DIR' in info:
        self.REMOTE_DIR = info['REMOTE_DIR']
      if 'WAIT_TIME' in info:
        self.WAIT_TIME = info['WAIT_TIME']
      if 'BAT_LOW' in info:
        self.BAT_LOW = info['BAT_LOW']
      if 'GIT_VER' in info:
        self.GIT_VER = info['GIT_VER']
      if 'BATCHARGED' in info:
        self.BATCHARGED = info['BATCHARGED']
      if 'TIME_ACTIVE' in info:
        self.TIME_ACTIVE = info['TIME_ACTIVE']
      newtag = self.fingerprint()
      if newtag != self.ETAG:
        self.ETAG = newtag
        self.saveconf()
      return False
    except Exception as e:
      print('Exception: ' + str(e))
      return True

  # save configuration receive from server
  def saveconf(self):
    try:
      f = open("/home/pi/savedconfig.txt", "w")
      f.write(self.REMOTE_DIR)
      f.write("\n")
      f.write(str(self.WAIT_TIME))
      f.write("\n")
      f.write(str(self.BAT_LOW))
      f.write("\n")
      f.write(self.GIT_VER)
      f.write("\n")
      f.write(str(self.BATCHARGED))
      f.write("\n")
      f.write(str(self.TIME_ACTIVE))
      f.write("\n")
      f.write(self.ETAG)
      f.write("\n")
      f.close()
    except Exception as e:
      print('Exception: ' + str(e))
      return True
    return False

  # read saved info
  def readsaved(self):
    try:
      f = open("/home/pi/savedconfig.txt", "r")
      i = 0
      for line in f:
        if i == 0:
          self.REMOTE_DIR=line.rstrip()
        if i == 1:
          self.WAIT_TIME=int(line.rstrip())
        if i == 2:
          self.BAT_LOW=int(line.rstrip())
        if i == 3:
          self.GIT_VER=line.rstrip()
        if i == 4:
          self.BATCHARGED=int(line.rstrip())
        if i == 5:
          self.TIME_ACTIVE=int(line.rstrip())
        if i == 6:
          self.ETAG=line.rstrip()
        i = i + 1
      f.close()
    except Exception as e:
      print('Exception: ' + str(e))
      return True
    return False

  #
  # read save version id
  def readsavedversion(self):
    version=""
    try:
      f = open("/home/pi/savedconfig.txt", "r")
      i = 0
      for line in f:
        if i == 3:
          version=line.rstrip()
          break
        i = i + 1
      f.close()
    except Exception as e:
      print('Exception: ' + str(e))
      return version
    return version

if __name__=='__main__':

  info = nodeinfo()
  print('server: ' + info.server)
  print('machine_id: ' + info.machine_id)
  if info.read():
    print("Failed")
  else:
    print(info.REMOTE_DIR)
    print(info.WAIT_TIME)
    print(info.BAT_LOW)
    print(info.GIT_VER)
    print(info.BATCHARGED)
    print(info.TIME_ACTIVE)
    info.saveconf()
    print("saved version: " + info.readsavedversion())
    print("Success")
