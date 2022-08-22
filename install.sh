#!/bin/bash

# install git and other tools we need.
sudo apt-get update
sudo apt-get -y install git cadaver libcamera-apps python3-smbus at
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
