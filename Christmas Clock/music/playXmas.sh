#ls /home/pi/music/*.wav | shuf -n 1 | xargs -I % aplay --nonblock "%"
ls /home/pi/music/*.wav | shuf -n 1 | xargs -I % sudo python /home/pi/lightshowpi/py/synchronized_lights.py --file="%"
