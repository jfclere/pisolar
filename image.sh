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

# check for the server (for one hour for the moment)
i=0
while [ $i -lt 60 ]
do
  /usr/bin/ping -c 1 -W 10 jfclere.myddns.me
  if [ $? -ne 0 ]; then
    /usr/bin/sleep 60
    /usr/bin/echo "Retrying ping jfclere.myddns.me"
    /usr/bin/sync
  else
    break
  fi
  i=`/usr/bin/expr $i + 1`
done
if [ $i -eq 60 ]; then
  /usr/bin/echo "ping jfclere.myddns.me failed stopping"
  # sleep 5 minutes and restart
  /home/pi/pisolar/writereg.py 6 300
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

code=`/usr/bin/curl -o /tmp/${MACHINE_ID} --silent --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/${MACHINE_ID}`
if [ $? -ne 0 ]; then
  # just retry
  code=`/usr/bin/curl -o /tmp/${MACHINE_ID} --silent --write-out '%{http_code}' https://jfclere.myddns.me/~jfclere/${MACHINE_ID}`
fi
if [ "${code}" == "200" ]; then
  # Read the values from the received file.
  /usr/bin/echo "200: YES!!!"
  /usr/bin/sync
  REMOTE_DIR=`/usr/bin/head -n 1 /tmp/${MACHINE_ID}`
  WAIT_TIME=`/usr/bin/tail -n 2 /tmp/${MACHINE_ID}| /usr/bin/head -n 1`
  BAT_LOW=`/usr/bin/tail -n 1 /tmp/${MACHINE_ID}`
  # read bat volts via i2c
  val=`/home/pi/pisolar/readreg.py 0`
  if [ $? -eq 0 ]; then
    /usr/bin/curl -o /dev/null --silent --head https://jfclere.myddns.me/~jfclere/report-${MACHINE_ID}-${val}
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
  # /usr/bin/libcamera-still -o /tmp/now.jpg
  /usr/bin/raspistill -o /tmp/now.jpg
  if [ $? -eq 0 ]; then
    /usr/bin/echo "mkcol ${REMOTE_DIR}" > /tmp/cmd.txt
    /usr/bin/echo "mkcol ${REMOTE_DIR}/${BASEDIR}" >> /tmp/cmd.txt
    /usr/bin/echo "mkcol ${REMOTE_DIR}/${DIR}" >> /tmp/cmd.txt
    /usr/bin/echo "put /tmp/now.jpg ${REMOTE_DIR}/${FILE}" >> /tmp/cmd.txt
    /usr/bin/python /home/pi/pisolar/bme280.py > /tmp/temp.txt
    if [ $? -eq 0 ]; then
      /usr/bin/echo "put /tmp/temp.txt ${REMOTE_DIR}/temp.txt" >> /tmp/cmd.txt
    fi
    /usr/bin/cadaver https://jfclere.myddns.me/webdav/ < /tmp/cmd.txt
  else
    /usr/bin/echo "Can't read image"
    /usr/bin/sync
  fi

  # sleep 5 minutes and restart
  if $IS_SOLAR; then
    wait_for=`/usr/bin/expr $WAIT_TIME \\* 60`
    /home/pi/pisolar/writereg.py 6 $wait_for
    if [ $? -ne 0 ]; then
      /usr/bin/echo "FAILED: can't return in wait mode!!!"
      /usr/bin/sync
      exit 0
    fi
    bat_low=`/home/pi/pisolar/readreg.py 2`
    if [ $? -eq 0 ]; then
      if [ $bat_low -ne $BAD_LOW ]; then
        /usr/bin/echo "Set bat_low $BAD_LOW (had: $bat_low)"
        /usr/bin/sync
        /home/pi/pisolar/writereg.py 2 $BAT_LOW
        if [ $? -eq 0 ]; then
          /usr/bin/echo "Set bat_low $BAD_LOW (had: $bat_low) FAILED"
          /usr/bin/sync
        fi 
      fi
    fi
    /usr/bin/echo "Stopping poweroff"
    /usr/bin/sync
    /usr/bin/sudo /usr/sbin/poweroff
  else
    /usr/bin/at -f /home/pi/pisolar/image.bash now + $WAIT_TIME minute
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
      /home/pi/pisolar/writereg.py 6 300 
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
