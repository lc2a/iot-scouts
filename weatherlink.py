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

parser = argparse.ArgumentParser()
parser.add_argument("-u", help="user for weatherlink api",type=str, required=True)
parser.add_argument("-p", help="password for weatherlink api",type=str, required=True)
parser.add_argument("-at", help="accesstoken for thingsboard",type=str, required=True)
parser.add_argument("-tb", help="thingsboard ip",type=str, required=True)

def ConvertToTimezone(timetoconvert, timezone):
    timezoneLocal = pytz.timezone(timezone)
    utc = pytz.utc
    timeLocal = utc.localize(timetoconvert).astimezone(timezoneLocal)
    return timeLocal.strftime("%s")+"000"


args = parser.parse_args()
user = args.u
password = args.p
THINGSBOARD_HOST = args.tb
ACCESS_TOKEN = args.at

parameters = ["temp_c", "wind_kt", "pressure_mb", "dewpoint_c", "heat_index_c", "relative_humidity"]
parameters2 = ["rain_day_in", "solar_radiation", "uv_index"]
attributes = ["latitude", "longitude", "station_id"]

#===========================================================

url="http://api.weatherlink.com/v1/NoaaExt.json?user={}&pass={}".format(user, password)
r = requests.get(url)
data = r.json()

newdata = {}
timestamp = email.utils.parsedate_to_datetime(data["observation_time_rfc822"]).strftime("%s")+"000"
print(timestamp)
newdata["ts"] = int(timestamp)
newdata["values"] = {}

for param in parameters:
    newdata["values"][param] = float(data[param])
for param in parameters2:
    newdata["values"][param] = float(data["davis_current_observation"][param])
print(newdata)


r = requests.post('http://'+THINGSBOARD_HOST+':8080/api/v1/'+ACCESS_TOKEN+'/telemetry', data = json.dumps(newdata))
print(r.text, r.status_code, r.raw)

newattrs = {}
for attr in attributes:
    newattrs[attr] = data[attr]

r = requests.post('http://'+THINGSBOARD_HOST+':8080/api/v1/'+ACCESS_TOKEN+'/attributes', data = json.dumps(newattrs))
print(r.text, r.status_code, r.raw)



