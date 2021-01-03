#!/bin/bash
while :
do
/opt/signal-cli-0.6.2/bin/signal-cli -u +123456789 receive -t 1800
mmv /home/pi/.local/share/signal-cli/attachments/\* /home/pi/signal/\#1.jpg
done
