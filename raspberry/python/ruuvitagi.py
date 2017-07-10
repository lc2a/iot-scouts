import paho.mqtt.client as mqtt
import json
import os
import time
import sys
import threading
import argparse
import codecs
from ruuvitag_sensor.ruuvi import RuuviTagSensor


parser = argparse.ArgumentParser()
parser.add_argument("-user", help="Username for MQTT broker",type=str, required=True)
parser.add_argument("-passw", help="Password for MQTT broker",type=str, required=True)
parser.add_argument("-ip", help="IP address of the MQTT broker",type=str, required=True)
parser.add_argument("-mac", help="Ruuvitag's MAC address",type=str, required=True)
args = parser.parse_args()
HOST = args.ip
mac = args.mac
INTERVAL = 30
sensor = RuuviTagSensor(mac)

def checkdata(data):
  return (-60 < data['temperature'] < 60) and (0 <= data['humidity'] <= 100) and (500 < data['pressure'] < 1500)

def SendData(data, topic, alert = False):
  global client
  data['serialNumber'] = "ruuvitag-{}".format(mac.replace(":",""))
  if not alert:
    data['ip'] = mac
    data['firmwarever'] = '0.2'
  print("SENDING DATA ", data)

  client.publish(topic, json.dumps(data))

def checkalert(data, alertmode):
  if data['acceleration'] > 1400:
    print("acc is over 1400")
    data2 = {}
    alertmode = True
    data2['alertstr'] = "Alert!: acceleration is {:.2f}".format(data['acceleration'])
    SendData(data2, "alert", True)

  elif (data['acceleration'] < 1400) and (alertmode == True):
    data2 = {}
    alertmode = False
    data2['alertstr'] = "Acceleration is back to normal"
    SendData(data2, "alert", True)

  return alertmode


while True:
  try:
    time.sleep(20)
    alertmode = False
    sensor_data = {}
    data = sensor.update()
    print(data)
    client = mqtt.Client()
    client.username_pw_set(username=args.user,password=args.passw)
    client.connect(HOST, 1883, 60)
    client.loop_start()
    sendtime = 0
    while True:
      data = sensor.update()
      sensor_data['temperature'] = data['temperature']
      sensor_data['humidity'] = data['humidity']
      sensor_data['pressure'] = data['pressure']
      sensor_data['acceleration'] = data['acceleration']
      sensor_data['battery'] = data['battery']

      if sendtime+INTERVAL < time.time():
        if checkdata(sensor_data):
            SendData(sensor_data, "ruuvi")
            sendtime = time.time()

      alertmode = checkalert(sensor_data, alertmode) 

      time.sleep(2)

    client.loop_stop()
    client.disconnect()
  except:
    print("restarting...", sys.exc_info()[0])
    client.loop_stop()
    client.disconnect()
    