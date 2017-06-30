#Gets data from atim api and posts it to our database, usage: python3 atim.py -u email_for_atim -p pass_for_atim
#working: authentication, parsing data to json format ready
#todo: post data to db

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

parser = argparse.ArgumentParser()
parser.add_argument("-u", help="email for atim api",type=str, required=True)
parser.add_argument("-p", help="password for atim api",type=str, required=True)

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

for device in devices:
    
    if device['devicename'][0:3] == "Sig":
        url2="https://api.atim.com/device/{}/channel/DIGITAL%20TEMPERATURE%201/message?limit=10".format(device['deviceid'])
        r = requests.get(url2, headers=headers)
        channeldatas = r.json()
        attributes_to_db = {}
        attributes_to_db['longitude'] = device['longitude']
        attributes_to_db['latitude'] = device['latitude']
        attributes_to_db['devicename'] = device['devicename']
        attributes_to_db['deviceid'] = device['deviceid']
        #send this to thingsboard as attributes
        print(attributes_to_db)
        for channeldata in channeldatas:
            values = {}
            values['temperature'] = channeldata['value']
            values['deviceid'] = channeldata['deviceid']
            values_to_db = {'ts':convert2epoch(channeldata['time'], 'Europe/Helsinki'), 'values': values}
            #send this to thingsboard as telemetry
            print(values_to_db)