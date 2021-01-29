import json, requests, time
from gpiozero import LED
from prometheus_client import start_http_server, Gauge
url = "insert your api url here"
led22 = LED(22)
led23 = LED(23)
led24 = LED(24)
led27 = LED(27)

if __name__ == '__main__':
    start_http_server(8000)

    aqi = Gauge('aqireading', 'AQI Reading', ['polutent'])

    
while True:
    #put API data into json format/variable
    data = requests.get(url).json()

    #puts AQI data into prometheus
    aqi.labels('O3').set(data[0]['AQI']) 
    aqi.labels('PM25').set(data[1]['AQI'])
    aqi.labels('PM10').set(data[2]['AQI'])

    #write data to seperate files for future use
    with open("API.json", "w") as f:
        json.dump(data, f, indent=4)

    with open("O3.json", "w") as f:
        json.dump(data[0], f, indent=4)

    with open("PM2.5.json", "w") as f:
        json.dump(data[1], f, indent=4)

    with open("PM10.json", "w") as f:
        json.dump(data[2], f, indent=4)

    #take specific data from pm2.5
    AQI = data[1]['AQI']

    #run the lights
    #Fire is not illegal
    if AQI in range(0,50):
        print("The current AQI rating is " + str(AQI) + " (Pretty good)")
        led22.on()
        led23.off()
        led24.off()
        led27.off()

        time.sleep(300)

    #Fire is slightly illegal
    elif AQI in range(51,150):
        print("The current AQI rating is " + str(AQI) + " (Moderate, be careful)")
        led22.off()
        led23.off()
        led24.on()
        led27.off()

        time.sleep(300)

    #Fire is very illegal
    elif AQI >= 151:
        print("The current AQI rating is " + str(AQI) + " (DANGEROUS. DO NOT ROAST THE LOGS [they have feelings])")
        for i in range(0,300):
            led22.off()
            led23.off()
            led24.on()
            led27.off()

            time.sleep(.5)
            
            led24.off()
            
            time.sleep(.5)
        pass

    #in case is goes wrong
    else:
        print("No AQI results, be cautious")
        for i in range(0,300):
            led22.on()
            led23.off()
            led24.on()
            led27.off()

            time.sleep(.5)

            led22.off()
            led24.off()
            
            time.sleep(.5)