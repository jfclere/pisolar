#!/bin/bash

#
# we will need the NetworkManager
sudo systemctl daemon-reload
sudo systemctl stop wpa_supplicant
sudo systemctl stop NetworkManager

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
       ssid=`echo $line | awk -F = ' { print $2 } '`
       has_ssid=true
       ;;
     *psk=*)
       psk=`echo $line | awk -F = ' { print $2 } '`
       has_psk=true
       ;;
     *key_mgmt=*)
       key_mgmt=`echo $line | awk -F = ' { print $2 } '`
       has_key_mgmt=true
       ;;
  esac
  if $has_ssid && $has_psk && $has_key_mgmt; then
    has_ssid=false
    has_psk=false
    has_key_mgmt=false
    name=`echo $ssid | awk -F \" ' { print $2 } '`
    if [ "$sid" = "$name" ]; then
      pass=`echo $psk | awk -F \" ' { print $2 } '`
      echo "$pass"
    fi
  fi
done < /home/pi/wpa_supplicant.conf
}

# configure by copying configuration
echo "install for wifi..."
sudo cp /home/pi/wpa_supplicant.conf /etc/wpa_supplicant/wpa_supplicant.conf
sudo chmod 600 /etc/wpa_supplicant/wpa_supplicant.conf
sudo rfkill unblock wifi
for filename in /var/lib/systemd/rfkill/*:wlan ; do
    echo 0 | sudo tee -a $filename
done
sudo systemctl start wpa_supplicant
sudo systemctl start NetworkManager
sleep 10
sudo systemctl status NetworkManager
sudo systemctl status wpa_supplicant
sudo rfkill list all
sudo rfkill unblock all
sudo rfkill list all
sudo nmcli radio wifi on
echo "install for wifi Done!!!"

# wait until wifi is started
while true
do
  sid=`nmcli -t -f SSID device wifi`
  if [ "$sid" = "" ]; then
    echo "waiting for wifi..."
    sudo nmcli -t -f SSID device wifi
    sudo rfkill list all
    echo "waiting for wifi!!!"
    sync
    sleep 10
  else
    iw dev wlan0 info
    echo "Wifi started!"
    break
  fi
done

# Try to connect to one of wifi we can see (Not needed???)
for sid in `nmcli -t -f SSID device wifi`
do
  echo "sid: $sid"
  pass=`getpass $sid`
  if [ "x$pass" = "x" ]; then
    echo "Ignore $sid not in our list"
  else
    echo "trying $sid $pass"
    sudo nmcli device wifi connect $sid password $pass
  fi
done

for run in {1..666}
do
  iw dev wlan0 info
  ssid=`iw dev wlan0 info | grep ssid | awk ' { print $2 } '`
  if [ "x$ssid" = "x" ]; then
    # sudo nmcli device wifi connect 3307X0354 password adelina2006
    sleep 10
    continue
  fi
  break
done

# install git and other tools we need.
sudo apt-get update
sudo apt-get -y install git cadaver libcamera-apps python3-smbus at python3-opencv
# checkout the repo
cd /home/pi
git clone https://github.com/jfclere/pisolar.git
# sudo raspi-config (activate camera and i2c)
# copy and test the ssh keys
# remove the password
# sudo passwd -d pi
# create the ~/.netrc file with
# machine MachineName
# login UserName
# password PassWord
# the httpd.conf conf piece is /etc/httpd/conf.d/webdav.conf

sudo passwd -d pi

# legacy camera
# sudo /usr/bin/raspi-config nonint do_legacy 0
# i2c
sudo /usr/bin/raspi-config nonint do_i2c 0

#
# Remove broken DST_Root_CA_X3.crt
sudo sed -i '/DST_Root_CA_X3.crt/d' /etc/ca-certificates.conf
sudo /usr/sbin/update-ca-certificates

sudo mkdir /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo apt -y --autoremove purge rsyslog
sudo cp pisolar/journald.conf /etc/systemd/journald.conf
sudo cp pisolar/logrotate.conf /etc/logrotate.conf
sudo cp pisolar/image.service /etc/systemd/system/
sudo systemctl enable image

sudo reboot
#wget -O bme280.py http://bit.ly/bme280py
# a python3 version is in the current repo...
