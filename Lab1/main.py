print("Xin chào ThingsBoard")
import paho.mqtt.client as mqttclient
import time
import json
import subprocess as sp
import re


BROKER_ADDRESS = "demo.thingsboard.io"
PORT = 1883
THINGS_BOARD_ACCESS_TOKEN = "0B4KhvgJhQX500lwFpJS"


def subscribed(client, userdata, mid, granted_qos):
    print("Subscribed...")


def recv_message(client, userdata, message):
    print("Received: ", message.payload.decode("utf-8"))
    temp_data = {'value': True}
    try:
        jsonobj = json.loads(message.payload)
        if jsonobj['method'] == "setValue":
            temp_data['value'] = jsonobj['params']
            client.publish('v1/devices/me/attributes', json.dumps(temp_data), 1)
    except:
        pass


def connected(client, usedata, flags, rc):
    if rc == 0:
        print("Thingsboard connected successfully!!")
        client.subscribe("v1/devices/me/rpc/request/+")
    else:
        print("Connection is failed")

# Get longitude latitude 
def getLocation():
    accuracy=3
    pshellcomm=["powershell"]
    pshellcomm.append('add-type -assemblyname system.device; ' \
        '$loc = new-object system.device.location.geocoordinatewatcher;' \
        '$loc.start(); ' \
        'while(($loc.status -ne "Ready") -and ($loc.permission -ne "Denied")) ' \
        '{start-sleep -milliseconds 100}; ' \
        '$acc = %d; ' \
        'while($loc.position.location.horizontalaccuracy -gt $acc) ' \
        '{start-sleep -milliseconds 100; $acc = [math]::Round($acc*1.5)}; ' \
        '$loc.position.location.latitude; ' \
        '$loc.position.location.longitude; ' \
        '$loc.position.location.horizontalaccuracy; ' \
        '$loc.stop()' % (accuracy))
    p = sp.Popen(pshellcomm, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT, text=True)
    (out, err) = p.communicate()
    out = re.split('\n', out)
    longitude = float(out[1])
    latitude = float(out[0])
    # print(out)
    return longitude,latitude




client = mqttclient.Client("Gateway_Thingsboard")
client.username_pw_set(THINGS_BOARD_ACCESS_TOKEN)

client.on_connect = connected
client.connect(BROKER_ADDRESS, 1883)
client.loop_start()

client.on_subscribe = subscribed
client.on_message = recv_message

temp = 30
humi = 50
light_intesity = 100
counter = 0



longitude=106.6297
latitude=10.8231
while True:
    collect_data = {'temperature': temp, 'humidity': humi, 'light':light_intesity,'longitude':longitude,'latitude':latitude}
    temp += 1
    humi += 1
    longitude,latitude=getLocation()
    light_intesity += 1
    client.publish('v1/devices/me/telemetry', json.dumps(collect_data), 1)
    print(collect_data)
    time.sleep(5)