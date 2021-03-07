# pisolar
software for ATTiny45 to power off the PI and power on after a while, the PI use I2C to start the power off/power on cycle.
Look to: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c to install the software on PI.
```bash
sudo apt install cadaver
sudo apt install python-smbus
```

# install the service
```bash
cp solar.service /etc/systemd/system/
systemctl enable solar
```
# connect the PI I2C to the ATTiny I2C (Pin 5 and 7)

# connect the ATTiny output(Pin 6)to IN(1) of the relay board.
The relay is used to cut the + cable of the USB that power the PI.

In fact I am not used a Relay but a MOSFET P and optocoupler but that is the same idea.

# Connect the + off the LiPo battery to 1M ohms + 220k ohms divisor
The Pin 2 of the ATTiny is connected after the 1M ohms resistor
220/(1000+220) = .180 (basic LiPo will gives 4.2 = .757, 2.7 = .487 values)


# start the ATTiny (plug it! to the 3.3V LiPo)

# Sending a picture to my server

I am using this to send a picture of the outside my window, taken by the RPI zero, ~ every 8 minutes to my server (using mod_dav and cadaver).

cadaver uses  ~/.netrc:

machine my_server_hostname

login my_user

passwd my_password
