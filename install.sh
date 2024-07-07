#!/bin/bash

# first install wifi information from /home/pi/wpa_supplicant.conf
# convert wpa_supplicant.conf in nmcli commands
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
    sudo nmcli connection add type wifi con-name $name wifi.ssid $ssid wifi-sec.key-mgmt $key_mgmt  wifi-sec.psk $psk
  fi
done < /home/pi/wpa_supplicant.conf

for run in {1..10}
do
  ssid=`iw wlan0 info | grep ssid | awk ' { print $2 } '`
  if [ "x$ssid" = "x" ]; then
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
