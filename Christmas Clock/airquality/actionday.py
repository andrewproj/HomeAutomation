import json, requests, time, io, PIL
from gpiozero import LED
from PIL import Image
from prometheus_client import start_http_server, Gauge

url = "https://www.airnowapi.org/aq/observation/zipCode/current/?parameters=PM25&format=application/json&zipCode=80017&distance=25&API_KEY=61E07A6E-679E-4058-8813-D40B0A8B6FEF"
green_left = LED(22)
green_right = LED(23)
red_left = LED(24)
red_right = LED(27)

if __name__ == '__main__':
    start_http_server(8000)

    aqi = Gauge('aqireading', 'AQI Reading', ['polutent'])
    actionday = Gauge('actionday', 'Action Day')

    while True:
            #try:
                aqi_json_data = requests.get(url).json()    
                aq_png_bytes = io.BytesIO(requests.get("https://www.colorado.gov/airquality/psi/adv.png").content)
                
                #puts AQI data into prometheus
                aqi.labels('O3').set(aqi_json_data[0]['AQI']) 
                aqi.labels('PM25').set(aqi_json_data[1]['AQI'])
                aqi.labels('PM10').set(aqi_json_data[2]['AQI'])

                aq_png_img = (PIL.Image.open(aq_png_bytes)).convert('RGB')
                aq_png_pixel_color = aq_png_img.getpixel((175, 55))
                
                if tuple(aq_png_pixel_color) == (0, 167, 215):
                    print("The current AQI rating is " + str(aqi_json_data[1]['AQI']) + " (Pretty good)")
                    actionday.set(0)
                    green_left.on()
                    green_right.on()
                    red_left.off()
                    red_right.off()
                else:
                    print("The current AQI rating is " + str(aqi_json_data[1]['AQI']) + " (Bad)")
                    actionday.set(1)
                    green_left.off()
                    green_right.off()
                    red_left.on()
                    red_right.on()
                
                time.sleep(300)
                
            #except:
            #    print('Error While Processing')
            #    time.sleep(10)
                
        
