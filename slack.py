import os
import slackclient
import requests
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("-u", help="Thingsboard username", type=str, required=True)
parser.add_argument("-p", help="Thingsboard password", type=str, required=True)
parser.add_argument("-t", help="Slack token", type=str, default=True)
args = parser.parse_args()
device_ids = {}
device_ids["ruuvitag"] = ["6a46de80-4aa8-11e7-a8f9-c53cc0543175",
                            "3a7c5150-4f60-11e7-a8f9-c53cc0543175"]
device_ids["sensehat"] = ["8990d510-3faa-11e7-a809-c53cc0543175", "8e4de7f0-3faa-11e7-a809-c53cc0543175",
                            "92feece0-3faa-11e7-a809-c53cc0543175", "92bd9180-4083-11e7-a809-c53cc0543175"]


def get_temp(device_name):
    global args, device_ids

    auth_url = "http://192.168.51.140:8080/api/auth/login"
    headers = {'Content-Type': 'application/json'}
    r = requests.post(auth_url, headers=headers,
                      data='{"username":"' + args.u + '", "password":"' + args.p + '"}')
    headers = {'Content-Type': 'application/json',
               'X-Authorization': 'Bearer {}'.format(r.json()['token'])}
    print(headers)
    stringit = ""
    a = 1
    print("ddddd", type(device_name))
    if device_name == "":
        stringit = "Available devices: "
        for device_name in device_ids.keys():
            stringit = stringit + device_name + ", "
        stringit = stringit[:-2]
    elif device_name.lower() in device_ids.keys():
        for device_id in device_ids[device_name.lower()]:
            url = "http://192.168.51.140:8080/api/plugins/telemetry/{}/values/timeseries?keys=temperature".format(
                device_id)
            r = requests.get(url, headers=headers)
            print(r.text)
            stringit = stringit + \
                "{}{} temperature: {} °C".format(device_name,
                    a, r.json()['temperature'][0]['value']) + "\n"
            a = a + 1
    else:
        stringit = "Device not found :("
    return stringit


#get_temp("sensehat")

VALET_SLACK_TOKEN = args.t
# initialize slack client
sc = slackclient.SlackClient(VALET_SLACK_TOKEN)
print(sc.api_call("auth.test"))

sc.rtm_connect()
while True:
    try:
        msg = sc.rtm_read()
        if msg != []:
            if msg[0]['text'][0:5] == "!temp":
                if len(msg[0]['text'].split(' ')) > 1:
                    temp_arg = msg[0]['text'].split(' ')[1]
                else:
                    temp_arg = ""
                #print(temp_arg)
                sc.rtm_send_message(msg[0]['channel'], get_temp(temp_arg))
            print(msg)
        else:
            # print("slep")
            time.sleep(1)
    except:
        time.sleep(1)
        pass
