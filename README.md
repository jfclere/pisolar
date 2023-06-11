# pisolar
software for ATTiny45 to power off the PI and power on after a while, the PI use I2C to start the power off/power on cycle.
Look to: https://learn.adafruit.com/adafruits-raspberry-pi-lesson-4-gpio-setup/configuring-i2c to install the software on PI.

# install arduino IDE on your laptop to build the ATTiny software.
See https://docs.arduino.cc/software/ide-v1/tutorials/Linux

# prepare the SDcard for the PI:
In the laptop make sure the SDcard is not mounted and copy the image.
```bash
dd bs=4M if=2022-04-04-raspios-bullseye-armhf-lite.img of=/dev/mmcblk0 conv=fsync
```
remove and reinsert the SDcard in the laptop (it will mount automatically otherwise mount boot and root by hands).
create the following files (See https://github.com/jfclere/pisolar#making-the-raspberry-an-object):
```
$HOME/wpa_supplicant.conf
$HOME/.netrc
$HOME/machine-id
```
make sure the $HOME/.ssh/id_rsa.pub contains you public ssh key.
run the preinstall script, the script assumes you have sudo permissions.
```bash
bash preinstall.sh
```
The preinstall install a service that will install all you need in PI the first time you boot it.
Make sure you unmount boot and root before removing the SDcard.

# Boot the PI with the SDcard
The install.sh script will run, be patient, make sure to keep the PI connected to the power.
If all works you should be able to ping the PI after a while and later to ssh to it.

# connect the PI I2C to the ATTiny I2C (Pin 5 and 7)

# connect the ATTiny output(Pin 6)to IN(1) of the relay board.
The relay is used to cut the + cable of the USB that power the PI.

In fact I am not used a Relay but a MOSFET P and optocoupler but that is the same idea.

# Connect the + off the LiPo battery to 1M ohms + 220k ohms divisor
The Pin 2 of the ATTiny is connected after the 1M ohms resistor
220/(1000+220) = .180

Basic LiPo will gives 4.2 = .757 when charged and 2.7 = .487 when empty.

We use the 1.1V ref on the ATTiny45 so charged: 4.2/.0059675 = 703 empty: 2.7/.0059675 = 452

# start the ATTiny (plug it! to the 3.3V LiPo)

# Sending a picture to my server

I am using this to send a picture of the outside my window, taken by the RPI zero, ~ every 8 minutes to my server (using mod_dav and cadaver).

cadaver uses  ~/.netrc:

machine my_server_hostname

login my_user

passwd my_password

# 3.3V to USB

Use 5V USB BOOST 500 MA in docs/Newversion.pdf it is connect to the EN (Enable pin)

# focus of the camera

Use V2.1 with the manual focus tool.
The V1.3 have the focus clued you need to break the clue to adjust the focus: remove the camera from the IC board, hold the lens with pliers and turn the camera anticlock wise until the clue cracks (be strong!), reassemble IC and camera, then ajust the focus with pliers gently. (I have used a piece of platic with a square hole to hold the camera).

# Making the raspberry an object

The raspberry is preinstalled (bash preinstall.sh) using data from your $HOME laptop:

## $HOME/.netrc file
Contains the information for cadaver (WebDAV client)
```
machine myserver.myddns.me
login httpduser
password httpdpasswd
```
The server myserver.myddns.me uses httpd with mod_dav (/etc/httpd/conf.d/webdav.conf)
```
<IfModule mod_dav_fs.c>
    DAVLockDB /var/lib/dav/lockdb
</IfModule>
Alias /webdav /home/webdav
<Directory /home/webdav>
    DAV On
    AuthType Basic
    AuthName WebDAV
    AuthUserFile /etc/httpd/conf/.htpasswd
    <LimitExcept GET POST OPTIONS>
        Require valid-user
    </LimitExcept>
    Options Indexes
    IndexOptions +FancyIndexing -FoldersFirst 
    IndexOrderDefault Descending Name
</Directory>
```
The user "httpduser" is created in the server myserver.myddns.me via htpasswd

## $HOME/wpa_supplicant.conf file
Contains the wifi information:
```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=CH
network={
  ssid="3307X0354"
  psk="jfc_secret_password"
  key_mgmt=WPA-PSK
}
```

## $HOME/machine-id
That is a unique id for the raspberry you are installing, it corresponds to a file in the server "myserver.myddns.me"
The files need to be accessible, test it with curl for example:
```bash
curl myserver.myddns.me/machines/68fa56d97f7c4ad18b377cc5780ee614
pi0neuchatel
10
600
```
The file $HOME/machine-id contains 68fa56d97f7c4ad18b377cc5780ee614.
The images from the camera will be saved under /home/webdav/pi0neuchatel
An image will be taken around every 10 minutes
And the raspberry won't be started if the battery voltage is lower than (600/167.57 ~ 3.58 Volt).

## $HOME/.ssh/id_rsa.pub
That allows you to ssh to the raspberry while it is up.

To keep the raspberry up for ever: move or remove the raspberry id file in the server "myserver.myddns.me"
```
mv /var/www/html/machines/68fa56d97f7c4ad18b377cc5780ee614 /var/www/html/machines/68fa56d97f7c4ad18b377cc5780ee614.save
```
Note that /var/www/html is the fedora location, sudo mkdir /var/www/html/machines to create, ajust the permissions if needed.


# Forcing modes
In the charger_receiver.ino:
```
// we have 3 states: auto, force on and force off.
#define AUTO  0x01
#define BATON 0x02
#define USBON 0x04
```
Default: 0x01 (AUTO)
To test:
```
pi@raspberrypi:~/pisolar $ /home/pi/pisolar/writereg.py 16 0
pi@raspberrypi:~/pisolar $ /home/pi/pisolar/readreg.py 16
0x0
```
Put the ATTiny in test mode.
To test the panel:
```
pi@raspberrypi:~/pisolar $ /home/pi/pisolar/writereg.py 16 2
pi@raspberrypi:~/pisolar $ /home/pi/pisolar/readreg.py 16
0x2
```
The panel will charge the battery.

# Other stuff
Some more things...

## Led indicator
Uses led.py and gpio=26 for activity (blue), gpio=13 for network OK (green) and gpio=19 to indicate it can read its configuration (red). A 330 Ohm resistor is on the minus ;-)

## Autoupdate for random PRI

The cron.sh can be used to update a remote RPI
