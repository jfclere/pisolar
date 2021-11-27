# install git and checkout the repo
# sudo apt-get install git cadaver python-smbus
# sudo raspi-config (activate camera and i2c)
# copy and test the ssh keys
# remove the password
# sudo passwd -d pi
# create the ~/.netrc file with
# machine MachineName
# login UserName
# password PassWord
# the httpd.conf conf piece is /etc/httpd/conf.d/webdav.conf

sudo mkdir /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo apt --autoremove purge rsyslog
sudo cp journald.conf /etc/systemd/journald.conf
sudo cp logrotate.conf /etc/logrotate.conf
sudo cp solar.service /etc/systemd/system/
sudo systemctl enable solar
wget -O bme280.py http://bit.ly/bme280py
