#!/bin/bash
REMOTE_DIR=grovemultigasv2
/usr/bin/echo "mkcol ${REMOTE_DIR}" >> /tmp/cmd.txt
/home/pi/pisolar/grovemultigasv2.py > /tmp/gas.txt
/usr/bin/echo "put /tmp/gas.txt ${REMOTE_DIR}/gas.txt" >> /tmp/cmd.txt
/usr/bin/cadaver https://jfclere.myddns.me/webdav/ < /tmp/cmd.txt
