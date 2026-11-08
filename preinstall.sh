# mount | grep mmcblk
# find boot and copy boot/wpa_supplicant.conf and touch boot/ssh
# and copy the ssh pub keys.
BOOT_DIR=`mount | grep vfat | grep bootfs | awk ' { print $3 } '`
ROOT_DIR=`mount | grep ext4 | grep rootfs | awk ' { print $3 } '`
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
  # that doesn't work with bookworm
  # cp $HOME/wpa_supplicant.conf $BOOT_DIR/
  sudo cp $HOME/wpa_supplicant.conf $ROOT_DIR/home/pi
  sudo chown 1000:1000 $ROOT_DIR/home/pi/wpa_supplicant.conf
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
sudo chmod 755 /run/media/jfclere/rootfs/home/pi
sudo chmod 600 /run/media/jfclere/rootfs/home/pi/.ssh/authorized_keys
sudo chmod 700 /run/media/jfclere/rootfs/home/pi/.ssh


# Copy the install we will run at the first boot.
sudo cp install.sh $ROOT_DIR/home/pi/
sudo cp install.service $ROOT_DIR/lib/systemd/system
sudo ln -s /lib/systemd/system/install.service $ROOT_DIR//etc/systemd/system/multi-user.target.wants

# Arrange shadow and passwd
sudo sed -i 's|^\(pi:[^:]*:[^:]*:[^:]*:[^:]*:[^:]*:\).*|\1/bin/bash|' /run/media/jfclere/rootfs/etc/passwd
sudo sed -i 's|^pi:![^:]*|pi:|' /run/media/jfclere/rootfs/etc/shadow

# Check syslog

echo "=== Systemd Journald Parsing Hierarchy (Last Line Wins) ==="

# 1. Read the main configuration file first
if [ -f "/run/media/jfclere/rootfs/etc/systemd/journald.conf" ]; then
    echo "[Main Config] /etc/systemd/journald.conf"
    grep -E '^Storage=' "/run/media/jfclere/rootfs/etc/systemd/journald.conf"
fi

# 2. Scan drop-ins in alphabetical execution order
# Systemd reads /usr/lib/... then /etc/...
find "/run/media/jfclere/rootfs/usr/lib/systemd/journald.conf.d/" "/run/media/jfclere/rootfs/etc/systemd/journald.conf.d/" -name "*.conf" 2>/dev/null | sort | while read -r file; do
    echo "[Drop-In File] ${file#/run/media/jfclere/rootfs}"
    grep -E '^Storage=' "$file"
done

