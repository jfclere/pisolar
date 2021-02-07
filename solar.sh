#!/bin/bash

/usr/bin/ping -c 1 -W 10 jfclere.myddns.me
if [ $? -ne 0 ]; then
  exit 0
fi
code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/off`
if [ "${code}" == "200" ]; then
  # Do what is neeede
  /usr/bin/echo "200: YES!!!"
  # tell arduino to wait 5 minutes and restart.
  /home/pi/pisolar/wait.py 5
  if [ $? -ne 0 ]; then
    exit 0
  fi
  /usr/sbin/poweroff
fi
