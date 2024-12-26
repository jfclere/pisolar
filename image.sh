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
IS_ERROR=false
SERVER=`/usr/bin/grep machine $HOME/.netrc | /usr/bin/awk ' { print $2 } '`
UPDATE_READY=false

# first install wifi information from /home/pi/wpa_supplicant.conf
# convert wpa_supplicant.conf in nmcli commands
getpass() {
sid=$1
has_ssid=false
has_psk=false
has_key_mgmt=false
while IFS= read -r line; do
  case "$line" in
     *ssid=*)
       ssid=`/usr/bin/echo $line | awk -F = ' { print $2 } '`
       has_ssid=true
       ;;
     *psk=*)
       psk=`/usr/bin/echo $line | awk -F = ' { print $2 } '`
       has_psk=true
       ;;
     *key_mgmt=*)
       key_mgmt=`/usr/bin/echo $line | awk -F = ' { print $2 } '`
       has_key_mgmt=true
       ;;
  esac
  if $has_ssid && $has_psk && $has_key_mgmt; then
    has_ssid=false
    has_psk=false
    has_key_mgmt=false
    name=`/usr/bin/echo $ssid | awk -F \" ' { print $2 } '`
    if [ "$sid" = "$name" ]; then
      pass=`/usr/bin/echo $psk | awk -F \" ' { print $2 } '`
      /usr/bin/echo "$pass"
    fi
  fi
done < /home/pi/wpa_supplicant.conf
}

#
# write the low: start the logic
write_low()
{
  newlow=$1
  bat_low=`/home/pi/pisolar/readreg.py 2`
  if [ $? -eq 0 ]; then
    if [ $bat_low -ne $newlow ]; then
      if [ $newlow -lt 500 -o $newlow -gt 600 ]; then
        newlow=500
      fi
      /usr/bin/echo "Set bat_low $mylow (had: $bat_low)"
      /usr/bin/sync
      /home/pi/pisolar/writereg.py 2 $mylow
      if [ $? -eq 0 ]; then
        /usr/bin/echo "Set bat_low $mylow (had: $bat_low) FAILED"
        /usr/bin/sync
      fi 
    fi
  fi
}
# write the high: stop charging
write_high()
{
  newhigh=$1
  bat_high=`/home/pi/pisolar/readreg.py 4`
  if [ $? -eq 0 ]; then
    if [ $bat_high -ne $newhigh ]; then
      if [ $newhigh -lt 600 -o  $newhigh -gt 800 ]; then
        newhigh=700
      fi
      /usr/bin/echo "Set bat_high $newhigh (had: $bat_high)"
      /usr/bin/sync
      /home/pi/pisolar/writereg.py 4 $newhigh
      if [ $? -eq 0 ]; then
        /usr/bin/echo "Set bat_high $newhigh (had: $bat_high) FAILED"
        /usr/bin/sync
      fi 
    fi
  fi
}

#
# Check for wifi
checkstartwifi()
{
  /usr/sbin/iw wlan0 link | /usr/bin/grep SSID > /dev/null
  if [ $? -ne 0 ]; then
    # We don't have a connection...
    # Check for bookworm, if yes wifi can be not yet configured.
    OSVER=`/usr/bin/grep VERSION_ID= /etc/os-release | /usr/bin/awk -F = ' { print $2 } '`
    OSVERID=`echo $OSVER`
    if [ $OSVERID -eq 12 ]; then
      /usr/bin/echo "bookworm!!!"
      # Try to connect to one of wifi we can see
      for sid in `/usr/bin/nmcli -t -f SSID device wifi`
      do
        /usr/bin/echo "sid: $sid"
        pass=`getpass $sid`
        if [ "x$pass" = "x" ]; then
          /usr/bin/echo "Ignore $sid not in our list"
        else
          /usr/bin/echo "trying $sid $pass"
          /usr/bin/sudo /usr/bin/nmcli device wifi connect $sid password $pass
        fi
      done
    fi
  fi
}

# create ssh if need
create_key()
{
  /usr/bin/echo "Checking ssh key"
  if [ ! -f /home/pi/.ssh/id_rsa.pub ]; then
    # Creates it
    /usr/bin/echo "Creating ssh key"
    /usr/bin/ssh-keygen -t rsa -f /home/pi/.ssh/id_rsa -N ""
  fi
  /usr/bin/scp  -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" /home/pi/.ssh/id_rsa.pub pi@$1:
  if [ $? -ne 0 ]; then
    /usr/bin/echo "put /home/pi/.ssh/id_rsa.pub id_rsa.pub.txt" > /tmp/cmd.txt
    /usr/bin/cadaver https://$1/webdav/ < /tmp/cmd.txt
  fi
}

# ssh to the server to allow a reversed connection (for 60 minutes) or wait 60 minutes
#
do_ssh()
{
  create_key $1
  i=0
  while [ $i -lt 60 ]
  do
    /usr/bin/ssh  -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" -R 2222:localhost:22 $1 -f 'sleep 3600'
    if [ $? -ne 0 ]; then
      /usr/bin/echo "ssh failed retrying... "
      sleep 60
    else
      break
    fi
    i=`/usr/bin/expr $i + 1`
  done
  /usr/bin/sync
}

#
# check for the server (for one hour for the moment)
i=0
while [ $i -lt 60 ]
do
  /usr/bin/ping -c 1 -W 10 ${SERVER}
  if [ $? -ne 0 ]; then
    /usr/bin/sleep 60
    # configuration needed?
    checkstartwifi
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
  BAT_HIGH=`/usr/bin/head -n 5 /tmp/${MACHINE_ID}| /usr/bin/tail -n 1`
  # read bat volts via i2c
  address=`/usr/sbin/ifconfig | /usr/bin/grep inet | /usr/bin/grep -v 127.0.0.1 | /usr/bin/grep -v inet6 | /usr/bin/awk '{ print $2 }'`
  val=`/home/pi/pisolar/readreg.py 0`
  if [ $? -eq 0 ]; then
    # the oldval is the bat volts at the time the ATtiny45 switched the USB on
    oldval=`/home/pi/pisolar/readreg.py 6`
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/reportold-${MACHINE_ID}-${oldval}
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${val}
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${address}
    /usr/bin/touch /home/pi/IS_SOLAR
  else
    if [ -f /home/pi/IS_SOLAR ]; then
      # we have a problem... the connection to the ATTiny I2C is lost...
      IS_ERROR=true
      /usr/bin/echo "ERROR readreg.py 0 retrying..."
      for run in {1..10}
      do
        /usr/bin/sleep 10
        val=`/home/pi/pisolar/readreg.py 0`
        if [ $? -eq 0 ]; then
          break
        fi
      done
    else
      IS_SOLAR=false
    fi
    /usr/bin/echo "ERROR readreg.py 0"
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${address}
    /usr/bin/sync
  fi

  # Create directory and report I2C error if needed
  /usr/bin/echo "mkcol ${REMOTE_DIR}" > /tmp/cmd.txt
  if $IS_ERROR; then
    FILE=`/usr/bin/date +%Y%m%d/%H00/%Y%m%d%H%M%S.txt`
    DIR=`/usr/bin/dirname ${FILE}`
    BASEDIR=`/usr/bin/dirname ${DIR}`
    /usr/bin/journalctl -u image > /tmp/error.txt
    /usr/bin/echo "mkcol ${REMOTE_DIR}/${BASEDIR}" >> /tmp/cmd.txt
    /usr/bin/echo "mkcol ${REMOTE_DIR}/${DIR}" >> /tmp/cmd.txt
    /usr/bin/echo "put /tmp/error.txt ${REMOTE_DIR}/${FILE}" >> /tmp/cmd.txt
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
    /usr/bin/python /home/pi/pisolar/bme280.py > /tmp/temp.txt
    if [ $? -eq 0 ]; then
      /usr/bin/echo "put /tmp/temp.txt ${REMOTE_DIR}/temp.txt" >> /tmp/cmd.txt
      /usr/bin/python /home/pi/pisolar/cv2isdark.py
      if [ $? -ne 0 ]; then
        # if the image is dark don't send it.
        /usr/bin/echo "mkcol ${REMOTE_DIR}/${BASEDIR}" >> /tmp/cmd.txt
        /usr/bin/echo "mkcol ${REMOTE_DIR}/${DIR}" >> /tmp/cmd.txt
        /usr/bin/echo "put /tmp/now.jpg ${REMOTE_DIR}/${FILE}" >> /tmp/cmd.txt
      fi
    else
      # Check if the image is dark
      /usr/bin/python /home/pi/pisolar/cv2isdark.py
      if [ $? -eq 0 ]; then
        # Dark image and no data to send: save energy do nothing...
        # sleep WAIT_TIME minutes and restart
        if $IS_SOLAR; then
          if [ $WAIT_TIME -lt 1 -o $WAIT_TIME -gt 1440 ]; then
            WAIT_TIME=60
          fi
          wait_for=`/usr/bin/expr $WAIT_TIME \\* 60`
          /home/pi/pisolar/writereg.py 8 $wait_for
          if [ $? -ne 0 ]; then
            /usr/bin/echo "FAILED: can't return in wait mode!!!"
            /usr/bin/sync
            exit 0
          fi
          /usr/bin/echo "Stopping poweroff"
          /usr/bin/sync
          /usr/bin/sudo /usr/sbin/poweroff
        fi
      else
        # if the image is NOT dark send it.
        /usr/bin/echo "mkcol ${REMOTE_DIR}/${BASEDIR}" >> /tmp/cmd.txt
        /usr/bin/echo "mkcol ${REMOTE_DIR}/${DIR}" >> /tmp/cmd.txt
        /usr/bin/echo "put /tmp/now.jpg ${REMOTE_DIR}/${FILE}" >> /tmp/cmd.txt
      fi
    fi
    /usr/bin/cadaver https://${SERVER}/webdav/ < /tmp/cmd.txt
  else
    /usr/bin/echo "Can't read image"
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${address}
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/reportold-${MACHINE_ID}-camerapb
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
    if [ $WAIT_TIME -lt 1 -o $WAIT_TIME -gt 1440 ]; then
       WAIT_TIME=60
    fi
    wait_for=`/usr/bin/expr $WAIT_TIME \\* 60`
    /home/pi/pisolar/writereg.py 8 $wait_for
    if [ $? -ne 0 ]; then
      /usr/bin/echo "FAILED: can't return in wait mode!!!"
      /usr/bin/sync
      exit 0
    fi
    # Ajust the low and high (if changed)
    write_low BAT_LOW
    write_high BAT_HIGH
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
    # We use crontab
    UPDATE_CRON=true
    /usr/bin/crontab -l > /tmp/crontab
    /usr/bin/echo "Setting crontab for $WAIT_TIME"
    if [ $WAIT_TIME -lt 1 -o $WAIT_TIME -gt 59 ]; then
      WAIT_TIME=1
    fi
    /usr/bin/grep image /tmp/crontab
    if [ $? -eq 0 ]; then
      # is the value OK
      oldwait=`/usr/bin/awk '{ print $1 }' /tmp/crontab`
      /usr/bin/echo "Old value: $oldwait"
      if [ "$oldwait" == "*" ]; then
        oldwait=1
      else
        oldwait=`/usr/bin/echo $l | /usr/bin/awk -F / ' { print $2 } '`
        /usr/bin/echo "Old value: $oldwait"
      fi
      if [ $oldwait -eq $WAIT_TIME ]; then
        /usr/bin/echo "Wait time unchanged"
        UPDATE_CRON=false
      fi
    fi
    if $UPDATE_CRON; then
      if [ $WAIT_TIME -eq 1 ]; then
        /usr/bin/echo "* * * * * /home/pi/pisolar/image.sh" > /tmp/crontab
        /usr/bin/crontab /tmp/crontab
        /usr/bin/echo "After crontab!"
      else
        /usr/bin/echo "*/$WAIT_TIME * * * * /home/pi/pisolar/image.sh" > /tmp/crontab
        /usr/bin/crontab /tmp/crontab
        /usr/bin/echo "After crontab"
      fi
    fi
    /usr/bin/echo "Done!"
  fi
else
  /usr/bin/echo "FAILED: code: ${code}!!!"
  /usr/bin/sync
  if [ "${code}" == "404" ]; then
    # No command file, maintenance mode
    /usr/bin/echo "Entrying maintenace mode"
    address=`/usr/sbin/ifconfig | /usr/bin/grep inet | /usr/bin/grep -v 127.0.0.1 | /usr/bin/grep -v inet6 | /usr/bin/awk '{ print $2 }'`
    /usr/bin/curl -o /dev/null --silent --head https://${SERVER}/machines/report-${MACHINE_ID}-${address}
    /usr/bin/sync
    # try to connect to the server or wait 60 minutes to allow manual connections...
    do_ssh ${SERVER}
    /usr/bin/sync
  else
    # Something wrong on the server
    /usr/bin/echo "Something wrong on the server ${code}"
  fi
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
