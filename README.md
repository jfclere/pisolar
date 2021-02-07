# pisolar
software for arduino to pover off the PI and power on after a while, the PI use I2C to start the power off/power on cycle.

# install the service
```bash
cp solar.service /etc/systemd/system/
systemctl enable solar
```
# connect the PI I2C to the arduino I2C

# connect the arduino output(11) to IN(1) of the relay board, the cut the + cable of the USB 

# start the arduino (plug it!)

# Done

