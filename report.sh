#!/bin/bash

code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/report`
if [ $? -ne 0 ]; then
  # just retry
  /usr/bin/sleep 60
  code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/report`
  if [ $? -ne 0 ]; then
    /usr/bin/echo "ERROR can't curl to server"
    /usr/bin/sync
    /usr/bin/sudo /usr/sbin/reboot
    exit 0
  fi
fi
if [ "${code}" != "200" ]; then
  /usr/bin/echo "Not configured! $code"
  /usr/bin/sync
  exit 0
fi

# make sure we have a time that makes sense
#
# Check the time
/usr/bin/timedatectl status | /usr/bin/grep synchronized | /usr/bin/grep yes > /dev/null
if [ $? -ne 0 ]; then
  /usr/bin/sudo /usr/bin/systemctl restart systemd-timesyncd.service
  /usr/bin/sleep 5
  /usr/bin/echo "Time synchronized"
  /usr/bin/sync
fi

# send the value (if working)
val=`/home/pi/pisolar/readreg.py 0`
if [ $? -eq 0 ]; then
  /usr/bin/curl -o /dev/null --silent --head https://jfclere.myddns.me/~jfclere/report${val}
else
  /usr/bin/echo "ERROR readreg.py 0"
  /usr/bin/sync
  /usr/bin/sudo /usr/sbin/reboot
  exit 0
fi

#
# read the image and send it.
/usr/bin/raspistill -o /tmp/now.jpg
/usr/bin/echo "put /tmp/now.jpg now.jpg" > /tmp/cmd.txt
/usr/bin/cadaver https://jfclere.myddns.me/webdav/ < /tmp/cmd.txt

# send again the value (if working)
val=`/home/pi/pisolar/readreg.py 0`
if [ $? -eq 0 ]; then
  /usr/bin/curl -o /dev/null --silent --head https://jfclere.myddns.me/~jfclere/report_2_${val}
else
  /usr/bin/echo "ERROR readreg.py 0"
  /usr/bin/sync
  /usr/bin/sudo /usr/sbin/reboot
  exit 0
fi

#
# sleep 6 minutes and restart
/home/pi/pisolar/writereg.py 6 360
if [ $? -ne 0 ]; then
  /usr/bin/echo "ERROR can't set waiting time"
  /usr/bin/sync
  /usr/bin/sudo /usr/sbin/reboot
  exit 0
fi
/usr/bin/echo "Done success"
/usr/bin/sync
/usr/bin/sudo /usr/sbin/poweroff
