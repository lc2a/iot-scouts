import sys
from bs4 import BeautifulSoup
import datetime
import pytz
import urllib.request
import json
import requests
import time
import collections
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-api", help="API key for fmi open data",type=str, required=True)
parser.add_argument("-p", help="place",type=str, required=True)
parser.add_argument("-parser", help="place",type=str, default="lxml-xml")
parser.add_argument("-at", help="accesstoken for thingsboard",type=str, required=True)
parser.add_argument("-tb", help="thingsboard ip",type=str, required=True)

args = parser.parse_args()

API_KEY = args.api
THINGSBOARD_HOST = args.tb
ACCESS_TOKEN = args.at
place = args.p

storedq_id = "fmi::observations::weather::timevaluepair"
parameters = ["temperature", "humidity", "pressure", "windspeedms"]

#===========================================================

parameters_str = ""
for parameter in parameters:
    parameters_str += parameter+","
parameters_str = parameters_str[:-1]

url = "http://data.fmi.fi/fmi-apikey/{}/wfs?request=getFeature&storedquery_id={}&parameters={}&place={}".format(API_KEY,storedq_id,parameters_str,place)
#print(url)
soup = BeautifulSoup(urllib.request.urlopen(url).read(), args.parser)
#print(soup)
tmp = soup.find_all('wfs:member')

tmptable = collections.defaultdict(dict)




def ConvertToTimezone(timetoconvert, timezone):
    timezoneLocal = pytz.timezone(timezone)
    utc = pytz.utc
    timeLocal = utc.localize(timetoconvert).astimezone(timezoneLocal)
    return timeLocal.strftime("%s")+"000"


for parametercount in range(len(parameters)):
    #print(parameters[parametercount])
    currentparameter = tmp[parametercount].find_all('wml2:point')
    for point in currentparameter:
        d1 = datetime.datetime.strptime(point.find('wml2:time').string,"%Y-%m-%dT%H:%M:%SZ")
        unixtimecode = ConvertToTimezone(d1, 'Europe/Helsinki')
        curparam = float(point.find('wml2:value').string)
        tmptable[unixtimecode].update({parameters[parametercount]: curparam})

        
#print(tmptable)
for timecode, parameters in tmptable.items():
    telemetrytable = {'values': parameters,'ts': timecode}
    print(telemetrytable)
    r = requests.post('http://'+THINGSBOARD_HOST+':8080/api/v1/'+ACCESS_TOKEN+'/telemetry', data = json.dumps(telemetrytable))