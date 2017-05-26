import sys
from bs4 import BeautifulSoup
import datetime
import pytz
import urllib.request
import json
import requests
import time
import collections


API_KEY = "c87db51d-6f6c-4b1a-8d90-076b32ccdf16"
storedq_id = "fmi::observations::weather::timevaluepair"
place = "jyvaskyla"
parameters = ["temperature", "humidity", "pressure", "windspeedms"]

#===========================================================

parameters_str = ""
for parameter in parameters:
    parameters_str += parameter+","
parameters_str = parameters_str[:-1]

url = "http://data.fmi.fi/fmi-apikey/{}/wfs?request=getFeature&storedquery_id={}&parameters={}&place={}".format(API_KEY,storedq_id,parameters_str,place)
print(url)
soup = BeautifulSoup(urllib.request.urlopen(url).read(), "html.parser")
tmp = soup.find_all('wfs:member')

tmptable = collections.defaultdict(dict)


THINGSBOARD_HOST = '192.168.51.140'
ACCESS_TOKEN = 'SPiMjsHa1WuZEN9kRlAT' # This must be changed

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
        curparam = point.find('wml2:value').string
        tmptable[unixtimecode].update({parameters[parametercount]: curparam})

        
#print(tmptable)
for timecode, parameters in tmptable.items():
    telematrytable = {'values': parameters,'ts': timecode}
    print(telematrytable)
    r = requests.post('http://'+THINGSBOARD_HOST+':8080/api/v1/'+ACCESS_TOKEN+'/telemetry', data = json.dumps(telematrytable))





