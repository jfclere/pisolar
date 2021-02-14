# pisolar
software for arduino to power off the PI and power on after a while, the PI use I2C to start the power off/power on cycle.
Look to: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c to install the software on PI.

# install the service
```bash
cp solar.service /etc/systemd/system/
systemctl enable solar
```
# connect the PI I2C to the arduino I2C

# connect the arduino output(11) to IN(1) of the relay board.
The relay is used to cut the + cable of the USB that power the PI.

# Connect the + off the LiPo battery to 1M ohms + 470k ohms divisor
The A5 of the arduino is connected after the 1M ohms resistor
270/(1000+270) = .2126 (basic LiPo will gives 4.2 = .893, 2.7 = .574 values)


# start the arduino (plug it!)

# Done

