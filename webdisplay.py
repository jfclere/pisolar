#!/usr/bin/python

import datetime
import mmap
import os
import requests
import time

import numpy as np
from PIL import Image

def send_to_fb(image_path):
    # 1. Load image and ensure it matches screen size (example: 1920x1080)
    # You can find your resolution using: cat /sys/class/graphics/fb0/virtual_size
    # pi@raspberrypi:~ $ cat /sys/class/graphics/fb0/virtual_size
    #1920,1080
    with open("/sys/class/graphics/fb0/virtual_size", "r") as f:
        width, height = map(int, f.read().strip().split(','))

    with open("/sys/class/graphics/fb0/bits_per_pixel", "r") as f:
        bpp = int(f.read().strip())
        bytes_per_pixel = bpp // 8

    print(f"Detected FB: {width}x{height} at {bpp}bpp")

    screen_width = 1920 
    screen_height = 1080
    
    img = Image.open(image_path).resize((screen_width, screen_height))
    
    # 2. Convert to BGRA or RGB32
    if bpp == 32:
        img = img.convert("RGBA")
        raw_data = img.tobytes()
    elif bpp == 24:
        img = img.convert("RGB")
        raw_data = img.tobytes()
    elif bpp == 16:
        pixels = np.array(img, dtype=np.uint16)
        r = (pixels[:,:,0] >> 3) << 11
        g = (pixels[:,:,1] >> 2) << 5
        b = (pixels[:,:,2] >> 3)
        rgb565 = r | g | b
        raw_data = rgb565.tobytes()
    else:
        print("Problem " + str(bpp))

    # 3. Open the framebuffer device
    with open("/dev/fb0", "wb") as fb:
        fb.write(raw_data)
        fb.flush()

def getetag(url):
  r = requests.head(url)
  if (r.status_code == 200):
    return r.headers['ETAG']
  return None

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
      f.flush()
  f.close()
  return 

if __name__=='__main__':
  d = datetime.datetime.now()
  url = "https://jfclere.myddns.me/webdav/pi0calella/" + d.strftime("%Y%m%d") + "/" + d.strftime("%H") + "00/"
  print(url)
  etag = getetag(url)
  print(etag)
  while True:
    time.sleep(10)
    d = datetime.datetime.now()
    url = "https://jfclere.myddns.me/webdav/pi0calella/" + d.strftime("%Y%m%d") + "/" + d.strftime("%H") + "00/"
    netag = getetag(url)
    # Time synchronization might return 404
    if netag is None:
      continue

    if netag == etag:
      continue
    else:
      print(netag)
      etag = netag
      latest = getlatestfile(url)
      if latest:
        url = url + latest
        print(url)
        downloadfile(url)
        send_to_fb("/tmp/now.jpg")
