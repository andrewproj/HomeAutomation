from prometheus_client import start_http_server, Gauge
from gpiozero import DiskUsage, LoadAverage, CPUTemperature
import time
import board
import busio
import adafruit_sht31d
import adafruit_tsl2591

if __name__ == '__main__':
    # Start up the server to expose the metrics.
    start_http_server(8000)
    
    # Connect to I2C sensors
    i2c = busio.I2C(board.SCL, board.SDA)
    sht31dSensor = adafruit_sht31d.SHT31D(i2c)  #Humidity / Temperature Sensor
    tsl12591Sensor = adafruit_tsl2591.TSL2591(i2c)   #Light Sensor
    
    # Define guages
    humidity = Gauge('grow_relative_humidity_percentage', 'Grow Tent Relative Humidity Percentage')
    temp = Gauge('grow_temperature', 'Grow Tent Temperature' ,['units'])
    light = Gauge('grow_light', 'Grow Tent Light', ['spectrum'])
    pi = Gauge('rpi', 'Raspberry Pi', ['internal_device'])
  
    # Capture Metrics
    while True:
        currentTemp = sht31dSensor.temperature
        
        temp.labels('fahrenheit').set((currentTemp * (9/5)) + 32 )
        temp.labels('celsius').set(currentTemp)            
        humidity.set(sht31dSensor.relative_humidity)   
        light.labels('total').set(tsl12591Sensor.lux) 
        light.labels('infrared').set(tsl12591Sensor.infrared) 
        light.labels('visable').set(tsl12591Sensor.visible) 
        light.labels('full_spectrum').set(tsl12591Sensor.full_spectrum)
        pi.labels('cpu_temperature_celsius').set(CPUTemperature().temperature)        
        pi.labels('load_average_5_min').set(LoadAverage().load_average)        
        pi.labels('disk_usage_percent').set(DiskUsage().usage)        
        
        time.sleep(1)
        
        