#!/bin/bash

code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/report`
if [ $? -ne 0 ]; then
  # just retry
  code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/report`
  if [ $? -ne 0 ]; then
    echo "ERROR can't curl to server"
    /usr/bin/sudo /usr/sbin/reboot
    exit 0
  fi
fi
if [ "${code}" != "200" ]; then
  echo "Not configured! $code"
  exit 0
fi

# send the value (if working)
high=`/home/pi/pisolar/wait.py 0`
if [ $? -eq 0 ]; then
  low=`/home/pi/pisolar/wait.py 1`
  if [ $? -eq 0 ]; then
    val=`/usr/bin/expr $high \\* 256`
    val=`/usr/bin/expr $val + $low`
    #echo "$high:$low:$val"
    /usr/bin/curl -o /dev/null --silent --head https://jfclere.myddns.me/~jfclere/report${val}
  else
    echo "ERROR low"
    /usr/bin/sudo /usr/sbin/reboot
  fi
else
  echo "ERROR high"
  /usr/bin/sudo /usr/sbin/reboot
  exit 0
fi

#
# read the image and send it.
/usr/bin/raspistill -o /tmp/now.jpg
/usr/bin/echo "put /tmp/now.jpg now.jpg" > /tmp/cmd.txt
/usr/bin/cadaver https://jfclere.myddns.me/webdav/ < /tmp/cmd.txt

#
# sleep 6 minutes and restart
/home/pi/pisolar/wait.py 6
if [ $? -ne 0 ]; then
  echo "ERROR can't set waiting time"
  /usr/bin/sudo /usr/sbin/reboot
  exit 0
fi
/usr/bin/sudo /usr/sbin/poweroff
