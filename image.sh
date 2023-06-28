#!/bin/bash

# We use /etc/machine-id to find waht we are ask to do...
# basically get the instructions from the server
# we receive it line by line
# 1 - directory where to push our images.
# 2 - time to take next picture.
# 3 - bat low (don't if the vbat is lower than this value).

# read machine-id and check for tmp file if we have not reboot we are probably on AC power device.
MACHINE_ID=`/usr/bin/cat /etc/machine-id`
IS_SOLAR=true
SERVER=`/usr/bin/grep machine $HOME/.netrc | /usr/bin/awk ' { print $2 } '`
UPDATE_READY=false

# check for the server (for one hour for the moment)
i=0
while [ $i -lt 60 ]
do
  /usr/bin/ping -c 1 -W 10 ${SERVER}
  if [ $? -ne 0 ]; then
    /usr/bin/sleep 60
    /usr/bin/echo "Retrying ping ${SERVER}"
    /usr/bin/sync
  else
    break
  fi
  i=`/usr/bin/expr $i + 1`
done
if [ $i -eq 60 ]; then
  /usr/bin/echo "ping ${SERVER} failed stopping"
  # sleep 5 minutes and restart
  /home/pi/pisolar/writereg.py 8 300
  if [ $? -ne 0 ]; then
    /usr/bin/echo "FAILED: can't return in wait mode!!!"
    /usr/bin/echo "Ping has failed"
    /usr/bin/sync
    exit 0
  fi
  /usr/bin/echo "Stopping poweroff"
  /usr/bin/sync
  /usr/bin/sudo /usr/sbin/poweroff
fi

#
# Check the time
/usr/bin/timedatectl status | /usr/bin/grep synchronized | /usr/bin/grep yes > /dev/null
if [ $? -ne 0 ]; then
  /usr/bin/sudo /usr/bin/systemctl restart systemd-timesyncd.service
  /usr/bin/sleep 5
fi

code=`/usr/bin/curl -o /tmp/${MACHINE_ID} --silent --write-out '%{http_code}' https://${SERVER}/machines/${MACHINE_ID}`
if [ $? -ne 0 ]; then
  # just retry
  code=`/usr/bin/curl -o /tmp/${MACHINE_ID} --silent --write-out '%{http_code}' https://${SERVER}/machines/${MACHINE_ID}`
fi
if [ "${code}" == "200" ]; then
  # Read the values from the received file.
  /usr/bin/echo "200: YES!!!"
  /usr/bin/sync
  REMOTE_DIR=`/usr/bin/head -n 1 /tmp/${MACHINE_ID}`
  WAIT_TIME=`/usr/bin/head -n 2 /tmp/${MACHINE_ID}| /usr/bin/tail -n 1`
  BAT_LOW=`/usr/bin/head -n 3 /tmp/${MACHINE_ID}| /usr/bin/tail -n 1`
  GIT_VER=`/usr/bin/head -n 4 /tmp/${MACHINE_ID} | /usr/bin/tail -n 1`
  # read bat volts via i2c
  val=`/home/pi/pisolar/readreg.py 0`
  if [ $? -eq 0 ]; then
    # the oldval is the bat volts at the time the ATtiny45 switched the USB on
    oldval=`/home/pi/pisolar/readreg.py 6`
    address=`/usr/sbin/ifconfig | /usr/bin/grep inet | /usr/bin/grep -v 127.0.0.1 | /usr/bin/grep -v inet6 | /usr/bin/awk '{ print $2 }'`
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/reportold-${MACHINE_ID}-${oldval}
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${val}
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${address}
  else
    IS_SOLAR=false
    /usr/bin/echo "ERROR readreg.py 0"
    /usr/bin/sync
  fi

  # take a picture and send it.
  FILE=`/usr/bin/date +%Y%m%d/%H00/%Y%m%d%H%M%S.jpg`
  DIR=`/usr/bin/dirname ${FILE}`
  BASEDIR=`/usr/bin/dirname ${DIR}`
  /usr/bin/echo "${FILE} ${DIR} ${BASEDIR}"
  /usr/bin/dmesg | /usr/bin/grep imx519
  if [ $? -eq 0 ]; then
    # we have autofocus camera
    /home/pi/pisolar/Autofocus.py
  fi
  # For old raspbian version (before bullseye)
  # /usr/bin/raspistill -o /tmp/now.jpg
  /usr/bin/libcamera-still -o /tmp/now.jpg
  if [ $? -eq 0 ]; then
    /usr/bin/echo "mkcol ${REMOTE_DIR}" > /tmp/cmd.txt
    /usr/bin/echo "mkcol ${REMOTE_DIR}/${BASEDIR}" >> /tmp/cmd.txt
    /usr/bin/echo "mkcol ${REMOTE_DIR}/${DIR}" >> /tmp/cmd.txt
    /usr/bin/echo "put /tmp/now.jpg ${REMOTE_DIR}/${FILE}" >> /tmp/cmd.txt
    /usr/bin/python /home/pi/pisolar/bme280.py > /tmp/temp.txt
    if [ $? -eq 0 ]; then
      /usr/bin/echo "put /tmp/temp.txt ${REMOTE_DIR}/temp.txt" >> /tmp/cmd.txt
    fi
    /usr/bin/cadaver https://${SERVER}/webdav/ < /tmp/cmd.txt
  else
    /usr/bin/echo "Can't read image"
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/reportold-${MACHINE_ID}-camerapb
    /usr/bin/echo "mkcol ${REMOTE_DIR}" > /tmp/cmd.txt
    /usr/bin/journalctl -u image > /tmp/temp.txt
    /usr/bin/echo "put /tmp/temp.txt ${REMOTE_DIR}/temp.txt" >> /tmp/cmd.txt
    /usr/bin/cadaver https://${SERVER}/webdav/ < /tmp/cmd.txt
    /usr/bin/sync
  fi

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
      /usr/bin/sync
      UPDATE_READY=true
    fi
  fi 

  # sleep 5 minutes and restart
  if $IS_SOLAR; then
    wait_for=`/usr/bin/expr $WAIT_TIME \\* 60`
    /home/pi/pisolar/writereg.py 8 $wait_for
    if [ $? -ne 0 ]; then
      /usr/bin/echo "FAILED: can't return in wait mode!!!"
      /usr/bin/sync
      exit 0
    fi
    bat_low=`/home/pi/pisolar/readreg.py 2`
    if [ $? -eq 0 ]; then
      if [ $bat_low -ne $BAT_LOW ]; then
        /usr/bin/echo "Set bat_low $BAT_LOW (had: $bat_low)"
        /usr/bin/sync
        /home/pi/pisolar/writereg.py 2 $BAT_LOW
        if [ $? -eq 0 ]; then
          /usr/bin/echo "Set bat_low $BAT_LOW (had: $bat_low) FAILED"
          /usr/bin/sync
        fi 
      fi
    fi
    if $UPDATE_READY; then
      /usr/bin/echo "Updated to $GIT_NEW"
      /usr/bin/rm -rf /home/pi/pisolar.${GIT_CUR}
      /usr/bin/mv /home/pi/pisolar /home/pi/pisolar.${GIT_CUR}
      /usr/bin/mv /home/pi/pisolar.new /home/pi/pisolar
    fi
    /usr/bin/echo "Stopping poweroff"
    /usr/bin/sync
    /usr/bin/sudo /usr/sbin/poweroff
  else
    if $UPDATE_READY; then
      /usr/bin/echo "Updated to $GIT_NEW"
      /usr/bin/rm -rf /home/pi/pisolar.${GIT_CUR}
      /usr/bin/mv /home/pi/pisolar /home/pi/pisolar.${GIT_CUR}
      /usr/bin/mv /home/pi/pisolar.new /home/pi/pisolar
      /usr/bin/sync
    fi
    #/usr/bin/at -f /home/pi/pisolar/image.bash now + $WAIT_TIME minute
  fi
else
  /usr/bin/echo "FAILED: code: ${code}!!!"
  /usr/bin/sync
  if [ "${code}" == "404" ]; then
    # No command file, maintenance mode
    /usr/bin/echo "Entrying maintenace mode"
    /usr/bin/sync
  else
    # Something wrong on the server
    val=`/home/pi/pisolar/readreg.py 0`
    if [ $? -eq 0 ]; then
      # wait 5 minutes
      /home/pi/pisolar/writereg.py 8 300 
      if [ $? -eq 0 ]; then
        /usr/bin/echo "FAILED: can't return in wait mode!!!"
        /usr/bin/sync
        exit 0
      else
        /usr/bin/echo "Stopping poweroff"
        /usr/bin/sync
        /usr/bin/sudo /usr/sbin/poweroff
      fi
    else
      # not solar just retry in a loop
      /usr/bin/echo "Stopping reboot"
      /usr/bin/sync
      /usr/bin/sudo /usr/sbin/reboot
    fi
  fi
fi
