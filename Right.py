#!/bin/bash

echo "Content-type: text/html"
echo ""

cmd=`basename $0 .py`

/home/pi/pisolar/motordrv8830.py $cmd
status=`/home/pi/pisolar/motordrv8830.py Status`
if [ -z "$status" ]; then
  echo "$cmd"
else
  echo "Failed: $cmd"
fi
