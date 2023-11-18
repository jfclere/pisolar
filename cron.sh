#!/bin/bash

# read machine-id
MACHINE_ID=`/usr/bin/cat /etc/machine-id`
SERVER=`/usr/bin/grep machine $HOME/.netrc | /usr/bin/awk ' { print $2 } '`
UPDATE_READY=false

code=`/usr/bin/curl -o /tmp/${MACHINE_ID} --silent --write-out '%{http_code}' https://${SERVER}/machines/${MACHINE_ID}`
if [ $? -ne 0 ]; then
  # just retry
  code=`/usr/bin/curl -o /tmp/${MACHINE_ID} --silent --write-out '%{http_code}' https://${SERVER}/machines/${MACHINE_ID}`
  if [ $? -ne 0 ]; then
    # failing twice problem?
    /usr/bin/echo "Something wrong..."
    /usr/bin/sync
    num=`/usr/bin/ls log.* | /usr/bin/wc -l`
    if [ $num -lt 10 ]; then
      /usr/bin/dmesg > log."`/usr/bin/date`"
    fi
    exit 1
  fi
fi
if [ "${code}" == "200" ]; then
  REMOTE_DIR=`/usr/bin/head -n 1 /tmp/${MACHINE_ID}`
  WAIT_TIME=`/usr/bin/head -n 2 /tmp/${MACHINE_ID}| /usr/bin/tail -n 1`
  BAT_LOW=`/usr/bin/head -n 3 /tmp/${MACHINE_ID}| /usr/bin/tail -n 1`
  GIT_VER=`/usr/bin/head -n 4 /tmp/${MACHINE_ID} | /usr/bin/tail -n 1`
  # chech if we need to upgrade
  GIT_CUR=`cd /home/pi/pisolar; /usr/bin/git log -1 --oneline | /usr/bin/awk ' { print $1 } '`

  if [ "$GIT_CUR" != "$GIT_VER" ]; then
    /usr/bin/rm -rf /home/pi/pisolar.new
    /usr/bin/cp -rp /home/pi/pisolar /home/pi/pisolar.new
    cd /home/pi/pisolar.new
    /usr/bin/git pull
    /usr/bin/git reset --hard $GIT_VER
    cd /home/pi/
    GIT_NEW=`cd /home/pi/pisolar.new; /usr/bin/git log -1 --oneline | /usr/bin/awk ' { print $1 } '`
    if [ "$GIT_VER" == "$GIT_NEW" ]; then
      # we have the new version checked out in /home/pi/pisolar.new
      /usr/bin/echo "Will to update to $GIT_NEW"
      /usr/bin/echo "Updated to $GIT_NEW"
      /usr/bin/rm -rf /home/pi/pisolar.${GIT_CUR}
      /usr/bin/mv /home/pi/pisolar /home/pi/pisolar.${GIT_CUR}
      /usr/bin/mv /home/pi/pisolar.new /home/pi/pisolar
      /usr/bin/sync
    fi
  fi
fi 
