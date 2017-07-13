import sys
import datetime
import pytz
import json
import requests
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-at", help="accesstoken for thingsboard",
                    type=str, required=True)
parser.add_argument("-tb", help="thingsboard ip", type=str, required=True)

args = parser.parse_args()

thingsboard_host = args.tb
access_token = args.at
datestr = time.strftime("%Y-%m-%d")

#===========================================================

url = "http://192.168.51.159:8080/harmitus/{}".format(datestr)
r = requests.get(url)
data = r.json()

for harmitus in data:
    newdata = {}
    newdata['values'] = {}
    if harmitus['endpoint'] == "Nu4W6wHRhTBifmy64ld74EqDWF4=":
        newdata["ts"] = harmitus['timestamp'] * 1000
        newdata['values']["harmitusLvl"] = harmitus['harmitusLvl']
        #newdata['values']["endpoint"] = harmitus['endpoint']
        r = requests.post('http://{}:8080/api/v1/{}/telemetry'.format(
            thingsboard_host, access_token), data=json.dumps(newdata))
        print(newdata)
