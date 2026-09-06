#!/bin/bash

# We use /etc/machine-id to find waht we are ask to do...
# basically get the instructions from the server
# we receive it line by line
# 1 - directory where to push our images.
# 2 - time to take next picture.
# 3 - bat low (don't if the vbat is lower than this value).

# read machine-id and check for tmp file if we have not reboot we are probably on AC power device.
MACHINE_ID=`/usr/bin/cat /etc/machine-id`
SERVER=`/usr/bin/grep machine $HOME/.netrc | /usr/bin/awk ' { print $2 } '`

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

# check the server key and add in .ssh/authorized_keys if needed.
add_server_key()
{
  code=`/usr/bin/curl https://$1/webdav/server.pub -o /tmp/server.pub --silent --write-out '%{http_code}'`
  if [ "${code}" == "200" ]; then
    key=`/usr/bin/cat /tmp/server.pub | /usr/bin/grep "ssh-rsa" | /usr/bin/awk ' { print $2 } '`
    if [ ! -z "${key}" ]; then
      authorized_keys=/home/pi/.ssh/authorized_keys
      /usr/bin/grep ${key} ${authorized_keys} 2>/dev/null 1>/dev/null
      if [ $? -ne 0 ]; then
        /usr/bin/echo "ssh-rsa ${key}" >> ${authorized_keys}
      fi
    fi
  fi
}


# ssh to the server to allow a reversed connection (for 60 minutes) or wait 60 minutes
#
do_ssh()
{
  # Done by hands... add_server_key $1
  # Done by hands...create_key $1
  i=0
  while [ $i -lt 60 ]
  do
    /usr/bin/ssh  -o "UserKnownHostsFile=/dev/null" -o "StrictHostKeyChecking=no" -R 2222:localhost:22 $1 -f 'sleep 3600'
    if [ $? -ne 0 ]; then
      /usr/bin/echo "ssh failed retrying... "
      /usr/bin/sync
      sleep 60
    else
      /usr/bin/echo "ssh start please connect to 2222 on $1... "
      /usr/bin/sync
      break
    fi
    i=`/usr/bin/expr $i + 1`
  done
  while true
  do
    /usr/bin/ps -ef | /usr/bin/grep "sleep 3600" | /usr/bin/grep -v grep >/dev/null 2>/dev/null
    if [ $? -ne 0 ]; then
      break
    fi
    sleep 60
  done
  /usr/bin/sync
}

# try to connect to the server or wait 60 minutes to allow manual connections...
ps -ef | grep ssh | grep -v grep | grep 2222
if [ $? -ne 0 ]; then
  do_ssh ${SERVER}
  /usr/bin/echo "Exiting maintenace mode"
  /usr/bin/sync
else
  /usr/bin/echo "Allready running"
fi
