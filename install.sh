sudo mkdir /var/log/journal
sudo systemd-tmpfiles --create --prefix /var/log/journal
sudo apt --autoremove purge rsyslog
sudo cp journald.conf /etc/systemd/journald.conf
sudo cp logrotate.conf /etc/logrotate.conf
sudo cp solar.service /etc/systemd/system/
sudo systemctl enable solar
wget -O bme280.py http://bit.ly/bme280py
