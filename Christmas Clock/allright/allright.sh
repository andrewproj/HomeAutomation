hour=$(date +%l)
ls /home/pi/allright/*.wav | shuf -n $hour | xargs -I % play -q %
