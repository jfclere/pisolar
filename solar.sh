#!/bin/bash

# check for the server (for one hour for the moment)
i=0
while [ $i -lt 60 ]
do
  /usr/bin/ping -c 1 -W 10 jfclere.myddns.me
  if [ $? -ne 0 ]; then
    /usr/bin/sleep 60
  else
    break
  fi
  i=`/usr/bin/expr $i + 1`
done
if [ $i -eq 60 ]; then
  # sleep 5 minutes and restart
  /home/pi/pisolar/wait.py 5
  if [ $? -ne 0 ]; then
    exit 0
  fi
  /usr/bin/sudo /usr/sbin/poweroff
fi

#
# Check the time
/usr/bin/timedatectl status | /usr/bin/grep synchronized | /usr/bin/grep yes > /dev/null
if [ $? -ne 0 ]; then
  /usr/bin/sudo /usr/bin/systemctl restart systemd-timesyncd.service
  /usr/bin/sleep 5
fi

code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/off`
if [ $? -ne 0 ]; then
  # just retry
  code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/off`
fi
if [ "${code}" == "200" ]; then
  # Do what is neeeded
  /usr/bin/echo "200: YES!!!"
  # tell arduino to wait 5 minutes and restart.
  high=`/home/pi/pisolar/wait.py 0`
  low=`/home/pi/pisolar/wait.py 1`
  val=`/usr/bin/expr $high \\* 256`
  val=`/usr/bin/expr $val + $low`
  /usr/bin/curl -o /dev/null --silent --head https://jfclere.myddns.me/~jfclere/off${val}
  #echo "$val $high $low"
  # take a picture and send it.
  FILE=`/usr/bin/date +%Y%m%d/%H00/%Y%m%d%H%M%S.jpg`
  DIR=`/usr/bin/dirname ${FILE}`
  BASEDIR=`/usr/bin/dirname ${DIR}`
  /usr/bin/echo "${FILE} ${DIR} ${BASEDIR}"
  /usr/bin/raspistill -o /tmp/now.jpg
  /usr/bin/echo "mkcol ${BASEDIR}" > /tmp/cmd.txt
  /usr/bin/echo "mkcol ${DIR}" >> /tmp/cmd.txt
  /usr/bin/echo "put /tmp/now.jpg ${FILE}" >> /tmp/cmd.txt
  /usr/bin/python /home/pi/pisolar/bme280.py > /tmp/temp.txt
  /usr/bin/echo "put /tmp/temp.txt temp.txt" >> /tmp/cmd.txt
  /usr/bin/cadaver https://jfclere.myddns.me/webdav/ < /tmp/cmd.txt
  # sleep 5 minutes and restart
  /home/pi/pisolar/wait.py 5
  if [ $? -ne 0 ]; then
    /usr/bin/echo "FAILED: can't return in wait mode!!!"
    exit 0
  fi
  /usr/bin/sudo /usr/sbin/poweroff
else
    /usr/bin/echo "FAILED: code: ${code}!!!"
fi
