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
import subprocess

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
  data['firmwarever'] = '0.35'
  client.publish('raspi', json.dumps(data))
  try:
    f = open('/home/pi/data/data.json', 'w+')
    f.write(str(json.dumps(data)))
    f.close()
  except:
    print("failed to save sensor data locally")


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

def hex2rgb(hexv):
    return (int(hexv[1:3], 16),int(hexv[3:5], 16),int(hexv[5:7], 16))

def getCPUtemp():
  temp = subprocess.getoutput("/opt/vc/bin/vcgencmd measure_temp")
  temp = temp.replace("temp=", "")
  temp = temp.replace("'C", "")
  return temp

def on_message(client, userdata, msg):
  print(msg.topic+" "+str(msg.payload))
  payload = json.loads(msg.payload.decode("utf-8"))
  if (payload['message'] == 'Brightness'):
    sense.low_light = (not sense.low_light)
  else:
    sense.show_message(payload['message'][:20], text_colour=hex2rgb(payload['color']))



print("Waiting for internet access...")
start = time.time()
end = time.time()
while end-start < 1:
  sense.show_message("Connecting...", text_colour=red)
  end = time.time()
sense.show_message(" OK ", text_colour=green)


sensor_data = {'temperature': 0, 'humidity': 0, 'pressure': 0}
next_reading = time.time() 
client = mqtt.Client()
client.on_message = on_message
# Set access token
client.username_pw_set(username=args.user,password=args.passw)

# Connect to Thingsboard using default MQTT port and 60 seconds keepalive interval
client.connect(HOST, 1883, 60)
client.loop_start()
client.subscribe('sensor/{}/request/#'.format(serialNumber))

try:
  count = 0
  while True:
    printPixels()
    getCPUtemp()
    humidity = round(sense.get_humidity(), 2)
    temperature = round(sense.get_temperature(), 2)
    air_pressure = round(sense.get_pressure(), 2)
    print(u"Temperature: {:g}\u00b0C, Humidity: {:g}%, Pressure: {}hpa".format(temperature, humidity, air_pressure))
    sensor_data['temperature'] = temperature
    sensor_data['humidity'] = humidity
    sensor_data['pressure'] = air_pressure
    sensor_data['CPUtemp'] = getCPUtemp()

    if 10 < air_pressure < 1500:
      #Sending humidity and temperature data to Thingsboard
      SendData(sensor_data)

    next_reading += INTERVAL
    sleep_time = next_reading-time.time()

    if sleep_time > 0:
      time.sleep(sleep_time)
except KeyboardInterrupt:
  pass

client.loop_stop()
client.disconnect()
