import requests
import time
import urllib3
import logging
from pydub import AudioSegment
from pydub.playback import play

if __name__ == '__main__':

  logging.basicConfig(filename='/home/pi/laundry/pylog.log', level=logging.DEBUG, format='%(asctime)s %(message)s')

  currentState_Washer = "ok"
  audioSample_Washer = AudioSegment.from_file('/home/pi/laundry/washer.wav', format="wav")

  currentState_Dryer = "ok"
  audioSample_Dryer = AudioSegment.from_file('/home/pi/laundry/dryer.wav', format="wav")
  
  urllib3.disable_warnings()
  while True:
    #---------------- Dryer ----------------
    try: 
      logging.debug("Preparing to Query Grafana Alert 2 - Dryer")
      logging.debug("Current State: (Washer) " + currentState_Dryer)
      r = requests.get('https://192.168.1.4:2443/grafana/api/alerts/2', verify=False)
      newState = r.json()["State"]
      logging.debug("New State: (Dryer) " +  newState)
      if newState == "ok" and currentState_Dryer == "alerting":
        for x in range (1,4):
          play(audioSample_Dryer)

      currentState_Dryer = newState
    except Exception:
      logging.exception(Exception)
      pass
      
    #---------------- Washer ----------------
    try: 
      logging.debug("Preparing to Query Grafana Alert 3 - Washer")
      logging.debug("Current State: (Washer) " + currentState_Washer)
      r = requests.get('https://192.168.1.4:2443/grafana/api/alerts/3', verify=False)
      newState = r.json()["State"]
      logging.debug("New State: (Washer) " + newState)
      if newState == "ok" and currentState_Washer == "alerting":
        for x in range (1,4):
          play(audioSample_Washer)
 
      currentState_Washer = newState
    except Exception:
      logging.exception(Exception)
      pass
   
    logging.debug("Sleeping for 30 Seconds")
    time.sleep(30)
