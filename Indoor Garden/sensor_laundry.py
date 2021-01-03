from prometheus_client import start_http_server, Gauge
from bluezero import microbit
import time
import datetime
import board
import busio
import math
import _thread
from collections import deque

def poll_accelerometer(ubit, name, gauge):
        queue = deque([],100)
        while True:
          x, y, z = ubit.accelerometer
          acceleration = math.sqrt(x**2 + y**2 + z**2)
          queue.append(acceleration)
          gauge.labels(name + '_immediate').set(acceleration)       
          gauge.labels(name + '_max').set(max(queue))

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8001) 
      
    #Connect to MicroBit #1 - Washer
    ubit_washer = microbit.Microbit(adapter_addr='XX:XX:XX:XX:XX:XX',
                         device_addr='XX:XX:XX:XX:XX:XX',
                         accelerometer_service=True,
                         button_service=False,
                         led_service=False,
                         magnetometer_service=False,
                         pin_service=False,
                         temperature_service=False)
    ubit_washer.connect()
        
    #Connect to MicroBit #2 - Dryer
    ubit_dryer = microbit.Microbit(adapter_addr='XX:XX:XX:XX:XX:XX',
                         device_addr='XX:XX:XX:XX:XX:XX',
                         accelerometer_service=True,
                         button_service=False,
                         led_service=False,
                         magnetometer_service=False,
                         pin_service=False,
                         temperature_service=False)
    ubit_dryer.connect()

    
    # Define guages
    accelerometer = Gauge('laundry_accelerometer', 'Laundry Accelerometer', ['machine']) 
   
    #Start threads to collect metrics
    _thread.start_new_thread( poll_accelerometer, (ubit_washer,'washer',accelerometer))
    _thread.start_new_thread( poll_accelerometer, (ubit_dryer,'dryer',accelerometer))
    
    while True:
        pass
    
    ubit_washer.disconnect()
    ubit_dryer.disconnect()
