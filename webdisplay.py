#!/usr/bin/python

import datetime
import requests
import time

def getetag(url):
  r = requests.head(url)
  return r.headers['ETAG']

def getlatestfile(url):
  r = requests.get(url)
  if (r.status_code == 200):
    for l in r.iter_lines():
      l = l.decode('ascii')
      if "IMG" not in l:
        continue
      else:
        l = l.split("a href=\"",1)[1]
        l = l.split("\"",1)[0]
        return l
  return None

def downloadfile(url):
  local_filename = "/tmp/now.jpg"
  r = requests.get(url)
  f = open(local_filename, 'wb')
  for chunk in r.iter_content(chunk_size=512 * 1024): 
    if chunk: # filter out keep-alive new chunks
      f.write(chunk)
  f.close()
  return 

if __name__=='__main__':
  d = datetime.datetime.now()
  url = "https://jfclere.myddns.me/webdav/pi0calella/" + d.strftime("%Y%m%d") + "/" + d.strftime("%H") + "00/"
  etag = getetag(url)
  print(etag)
  while True:
    time.sleep(10)
    netag = getetag(url)
    if netag == etag:
      continue
    else:
      print(netag)
      latest = getlatestfile(url)
      if latest:
        url = url + latest
        print(url)
        downloadfile(url)
      break
