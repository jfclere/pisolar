#!/bin/bash

# Shell to update the version we are using.

GIT_VER=$1
UPDATE_READY=false

# chech if we need to upgrade
GIT_CUR=`cd /home/pi/pisolar; /usr/bin/git log -1 --oneline | /usr/bin/awk ' { print $1 } '`
echo "GIT_VER: ${GIT_VER} GIT_CUR: ${GIT_CUR}"
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

if $UPDATE_READY; then
  /usr/bin/echo "Updated to $GIT_NEW"
  /usr/bin/rm -rf /home/pi/pisolar.${GIT_CUR}
  /usr/bin/mv /home/pi/pisolar /home/pi/pisolar.${GIT_CUR}
  /usr/bin/mv /home/pi/pisolar.new /home/pi/pisolar
  /usr/bin/sync
fi
