import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
from sense_hat import SenseHat
import json
import os
import time
import sys
import threading
import netifaces as ni
import argparse
import codecs

INTERVAL=30

sense = SenseHat()

parser = argparse.ArgumentParser()
parser.add_argument("-user", help="Username for MQTT broker",type=str, required=True)
parser.add_argument("-passw", help="Password for MQTT broker",type=str, required=True)
parser.add_argument("-ip", help="IP address of the MQTT broker",type=str, required=True)
args = parser.parse_args()
HOST = args.ip

try:
  with open('/sys/class/net/eth0/address') as f:
    serialNumber = "raspi-"+codecs.encode(f.read().strip().replace(":", ""), "rot-13")
except: 
    print('Failed to read MAC address')

def SendData(data):
  global serialNumber, client
  data['serialNumber'] = serialNumber
  data['ip'] = getIp()
  data['firmwarever'] = '0.2'
  client.publish('raspi', json.dumps(data))


def printPixels():
  X = [0, 255, 0]  # Green
  O = [0, 0, 0] # White

  pixel_fin = [
  X, O, O, O, O, O, O, X,
  O, O, O, O, O, O, O, O,
  O, O, O, O, O, O, O, O,
  O, O, O, X, X, O, O, O,
  O, O, O, X, X, O, O, O,
  O, O, O, O, O, O, O, O,
  O, O, O, O, O, O, O, O,
  X, O, O, O, O, O, O, X
  ]
  sense.set_pixels(pixel_fin)
  time.sleep(2)
  sense.clear()

red = (255, 0, 0)
green = (0, 255, 0)

print("Waiting for internet access...")
start = time.time()
end = time.time()
while end-start < 30:
  sense.show_message("Connecting...", text_colour=red)
  end = time.time()
sense.show_message(" OK ", text_colour=green)


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


sensor_data = {'temperature': 0, 'humidity': 0, 'pressure': 0}
next_reading = time.time() 
client = mqtt.Client()
client.on_message = on_message
# Set access token
client.username_pw_set(username=args.user,password=args.passw)

# Connect to Thingsboard using default MQTT port and 60 seconds keepalive interval
client.connect(HOST, 1883, 60)
client.loop_start()
client.subscribe('sensor/' + serialNumber + '/request/+/+')

def getIp():
# Try to get wlan0, otherwise eth0
  global client
  try:
    ni.ifaddresses('wlan0')
    ip = ni.ifaddresses('wlan0')[2][0]['addr']
  except:
    ni.ifaddresses('eth0')
    ip = ni.ifaddresses('eth0')[2][0]['addr']
  return ip


try:
  count = 0
  while True:
    printPixels()
    humidity = round(sense.get_humidity(), 2)
    temperature = round(sense.get_temperature(), 2)
    air_pressure = round(sense.get_pressure(), 2)
    print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%, Pressure: {}hpa".format(temperature, humidity, air_pressure))
    sensor_data['temperature'] = temperature
    sensor_data['humidity'] = humidity
    sensor_data['pressure'] = air_pressure
    if 10 < air_pressure < 1500:
      #Sending humidity and temperature data to Thingsboard
      SendData(sensor_data)

    next_reading += INTERVAL
    sleep_time = next_reading-time.time()

    count += 1
    if count > 10:
      getIp()
      count = 0

    if sleep_time > 0:
      time.sleep(sleep_time)
except KeyboardInterrupt:
  pass

client.loop_stop()
client.disconnect()