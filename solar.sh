#!/bin/bash

/usr/bin/ping -c 1 -W 10 jfclere.myddns.me
if [ $? -ne 0 ]; then
  exit 0
fi
code=`/usr/bin/curl -o /dev/null --silent --head --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/off`
if [ "${code}" == "200" ]; then
  # Do what is neeeded
  /usr/bin/echo "200: YES!!!"
  # tell arduino to wait 5 minutes and restart.
  high=`/home/pi/pisolar/wait.py 0`
  low=`/home/pi/pisolar/wait.py 1`
  val=`expr $high \\* 256`
  val=`expr $val + $low`
  /usr/bin/curl -o /dev/null --silent --head https://jfclere.myddns.me/~jfclere/off${val}
  #echo "$val $high $low"
  # take a picture and send it.
  FILE=`/usr/bin/date +%Y%m%d/%H00/%Y%m%d%H%M%S.jpg`
  DIR=`/usr/bin/dirname ${FILE}`
  BASEDIR=`/usr/bin/dirname ${DIR}`
  /usr/bin/echo "${FILE} ${DIR} ${BASEDIR}"
  /usr/bin/raspistill -o /tmp/now.jpg
  /usr/bin/echo "mkcol ${BASEDIR}" > cmd.txt
  /usr/bin/echo "mkcol ${DIR}" >> cmd.txt
  /usr/bin/echo "put /tmp/now.jpg ${FILE}" >> cmd.txt
  /usr/bin/cadaver -r /home/pi/.netrc https://jfclere.myddns.me/webdav/ < cmd.txt
  # sleep 5 minutes and restart
  /home/pi/pisolar/wait.py 5
  if [ $? -ne 0 ]; then
    exit 0
  fi
  /usr/sbin/poweroff
fi
