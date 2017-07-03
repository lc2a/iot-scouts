#Gets data from atim api and posts it to our database, usage: python3 atim.py -u email_for_atim -p pass_for_atim -at access_token -ip ip_to_tb
import sys
import datetime
import pytz
import urllib.request
import json
import requests
import time
import collections
import argparse
import re
import email.utils
import base64
import paho.mqtt.client as mqtt

parser = argparse.ArgumentParser()
parser.add_argument("-u", help="email for atim api",type=str, required=True)
parser.add_argument("-p", help="password for atim api",type=str, required=True)
parser.add_argument("-at", help="access token for the mqtt gateway in thingsboard",type=str, required=True)
parser.add_argument("-ip", help="ip to thingsboard",type=str, required=True)

args = parser.parse_args()

auth_code = base64.b64encode('{}:{}'.format(args.u, args.p).encode()).decode()


def convert2epoch(timetoconvert, timezone):
    d1 = datetime.datetime.strptime(timetoconvert,"%Y-%m-%dT%H:%M:%S.000Z")
    timezoneLocal = pytz.timezone(timezone)
    utc = pytz.utc
    timeLocal = utc.localize(d1).astimezone(timezoneLocal)
    return int(timeLocal.strftime("%s")+"000")


#===========================================================
url="https://api.atim.com/device"

headers = {'Authorization': 'Basic {}'.format(auth_code)}
r = requests.get(url, headers=headers)
devices = r.json()

client = mqtt.Client()
client.username_pw_set(username=args.at)
client.connect(args.ip, 1883, 60)
client.loop_start()

for device in devices:
    
    if device['devicename'][0:3] == "Sig":
        url2="https://api.atim.com/device/{}/channel/DIGITAL%20TEMPERATURE%201/message".format(device['deviceid'])
        r = requests.get(url2, headers=headers)
        channeldatas = r.json()
        attributes_to_db = {}
        attributes_to_db['longitude'] = device['longitude']
        attributes_to_db['latitude'] = device['latitude']
        attributes_to_db['devicename'] = device['devicename']
        serialNumber = "sig-{}".format(device['deviceid'])
        attributes_to_db['serialNumber'] = serialNumber
        client.publish('v1/gateway/connect', json.dumps({'device': serialNumber}))
        client.publish('v1/gateway/attributes', json.dumps(attributes_to_db))
        
        print(attributes_to_db)

        for channeldata in channeldatas:
            values = {}
            values['temperature'] = channeldata['value']
            values_to_db = {serialNumber: [{'ts':convert2epoch(channeldata['time'], 'Europe/Helsinki'), 'values': values}]}   
            client.publish('v1/gateway/telemetry', json.dumps(values_to_db))
            print(values_to_db)

        client.publish('v1/gateway/disconnect', json.dumps({'device': serialNumber}))