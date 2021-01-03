ls /home/pi/allright/*.wav | shuf -n 1 | xargs -I % play -q %
