import paho.mqtt.client as mqtt
import json
import os
import time
import sys
import threading
import argparse
import codecs
from ruuvitag_sensor.ruuvi import RuuviTagSensor

INTERVAL = 30

parser = argparse.ArgumentParser()
parser.add_argument("-user", help="Username for MQTT broker",type=str, required=True)
parser.add_argument("-passw", help="Password for MQTT broker",type=str, required=True)
parser.add_argument("-ip", help="IP address of the MQTT broker",type=str, required=True)
parser.add_argument("-mac", help="Ruuvitag's MAC address",type=str, required=True)
args = parser.parse_args()
HOST = args.ip
mac = args.mac
sensor = RuuviTagSensor(mac)
running = True

#filter out bad readings
def checkdata(data):
  return (-100 < data['temperature'] < 100) and (0 <= data['humidity'] <= 100) and (500 < data['pressure'] < 1500)

def senddata(data, topic):
  global client
  data['serialNumber'] = "ruuvitag-{}".format(mac.replace(":",""))
  data['ip'] = mac
  data['firmwarever'] = '0.3'
  print("SENDING DATA ", data)

  client.publish(topic, json.dumps(data))

#ignores interval setting if certain limit are crossed
def checkalert(data):
  return (data['acceleration'] > 1400) or (data['temperature'] > 90)

def closeconnection():
  global client
  client.loop_stop()
  client.disconnect()
  return False

while running:
  try:
    print("starting...")
    time.sleep(10)
    alertmode = False
    sensor_data = {}
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

      if (sendtime+INTERVAL < time.time()) or (checkalert(sensor_data)):
        if checkdata(sensor_data):
            senddata(sensor_data, "ruuvi")
            sendtime = time.time()

      time.sleep(2)

  except (KeyboardInterrupt, SystemExit):
    print("closing")
    running = closeconnection()
  except:
    print("unexpected error: ", sys.exc_info()[0])
    client.loop_stop()
    client.disconnect()
    