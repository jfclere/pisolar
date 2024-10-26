#!/usr/bin/python

import time
import math
import sys
import os
import requests
import socket

from nodeinfo import nodeinfo

#
# This report send a file to the server
#

def main():
  info = nodeinfo()
  print('server: ' + info.server)
  print('machine_id: ' + info.machine_id)
  if info.read():
    print("Failed no info!")
    exit()
  else:
    print(info.REMOTE_DIR)
    print(info.WAIT_TIME)
    print(info.BAT_LOW)
    print(info.GIT_VER)
    print(info.BATCHARGED)
    print(info.TIME_ACTIVE)

  headers = {'Content-type': 'text/plain'}
  path = "/tmp/dongle1.txt"
  url = "https://" + info.server + "/webdav/" + info.REMOTE_DIR + "/temp.txt"
  print("sending: ", path, " to: ", url)
  requests.put(url, data=open(path, 'r'), headers=headers, auth=(info.login, info.password))

  print("Done")

if __name__ == "__main__":
  main()
