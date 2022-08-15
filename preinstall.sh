# mount | grep mmcblk
# find boot and copy boot/wpa_supplicant.conf and touch boot/ssh
# and copy the ssh pub keys.
BOOT_DIR=`mount | grep mmcblk | grep boot | awk ' { print $3 } '`
ROOT_DIR=`mount | grep mmcblk | grep rootfs | awk ' { print $3 } '`
if [ -z $BOOT_DIR ]; then
  echo "BOOT_DIR empty!"
  exit 1
fi
if [ -z $ROOT_DIR ]; then
  echo "ROOT_DIR empty!"
  exit 1
fi
touch $BOOT_DIR/ssh
if [ -f $HOME/wpa_supplicant.conf ]; then
  cp $HOME/wpa_supplicant.conf $BOOT_DIR/
else
  echo "Missing $HOME/wpa_supplicant.conf"
fi
if [ -f $HOME/.netrc ]; then
  sudo cp $HOME/.netrc $ROOT_DIR/home/pi
  sudo chown 1000:1000 $ROOT_DIR/home/pi/.netrc
else
  echo "Missing $HOME/.netrc"
fi
if [ -f $HOME/machine-id ]; then
  sudo cp $HOME/machine-id $ROOT_DIR/etc
else
  echo "Missing $HOME/machine-id"
fi

# copy the ssh key
sudo mkdir $ROOT_DIR/home/pi/.ssh
sudo chown 1000:1000 $ROOT_DIR/home/pi/.ssh
sudo cp $HOME/.ssh/id_rsa.pub $ROOT_DIR/home/pi/.ssh/authorized_keys
sudo chown 1000:1000 $ROOT_DIR/home/pi/.ssh/authorized_keys

# Copy the install we will run at the first boot.
sudo cp install.sh $ROOT_DIR/home/pi/
sudo cp install.service $ROOT_DIR/lib/systemd/system
sudo ln -s /lib/systemd/system/install.service $ROOT_DIR//etc/systemd/system/multi-user.target.wants

