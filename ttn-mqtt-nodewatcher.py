from __future__ import print_function
# https://www.thethingsnetwork.org/forum/t/a-python-program-to-listen-to-your-devices-with-mqtt/9036/6
# Get data from MQTT server
# Run this with python 3, install paho.mqtt prior to use
import paho.mqtt.client as mqtt
import json
import base64
import collections
import hashlib
import hmac
import requests
import yaml

#TTN application details
APPEUI  = "INSERTAPPEUI"
APPID   = "INSERTAPPID"
PSW     = 'INSERTACCESSKEY'

#Nodewatcher server details
host    = 'push.nodes.wlan-si.net'
uuid    = 'INSERTNWUUID'
key     = 'INSERTNWHMACKEY'

def nodewatcher_uri_for_node(uuid):
    """Generate nodewatcher push URI for a specific node.

    :param uuid: node uuid
    """
    return 'http://{host}/push/http/{uuid}'.format(
        host=host,
        uuid=uuid,
    )

def nodewatcher_push(uuid, body, ignore_errors=True):
    """Push data to nodewatcher server.

    :param uuid: node uuid
    :param body: correctly formatted request body
    :param ignore_errors: whether errors should be silently ignored
    """
    body = json.dumps(body)
    key_bytes = bytes(key).encode('latin-1')
    data_bytes = bytes(body).encode('latin-1')

    signature = base64.b64encode(hmac.new(key_bytes, data_bytes, hashlib.sha256).digest())

    try:
        requests.post(
            nodewatcher_uri_for_node(uuid),
            data=body,
            headers={
                'X-Nodewatcher-Signature-Algorithm': 'hmac-sha256',
                'X-Nodewatcher-Signature': signature,
            }
        )
    except:
        if not ignore_errors:
            raise

# gives connection message
def on_connect(mqttc, mosq, obj,rc):
    print("Connected with result code:"+str(rc))
    # subscribe for all devices of user
    mqttc.subscribe('+/devices/+/up')

# gives message from device
def on_message(mqttc,obj,msg):
    try:
        # Get the message payload
        x = json.loads(msg.payload.decode('utf-8'))
        # Parse fields of metadata and payload
        device = x["dev_id"]
        counter = x["counter"]
        payload_raw = x["payload_raw"]
        payload_fields = x["payload_fields"]
        datetime = x["metadata"]["time"]
        gateways = x["metadata"]["gateways"]

        # Create the body for nodewatcher push
        body = {
            'sensors.generic': {
                '_meta': {'version': 1}
            }
        }

        # print for every gateway that has received the message and extract RSSI
        for gw in gateways:
            gateway_id = gw["gtw_id"]
            rssi = gw["rssi"]
            body['sensors.generic'][device+'_'+gateway_id+'_rssi']={'name': gateway_id+'_rssi', 'unit': device+' dBm','value': rssi,'group': device+'_rssi'}

            #Printable output logged to a file
            output = datetime + ", " + device + ", " + str(counter) + ", "+ gateway_id + ", "+ str(rssi) + ", " + str(payload_fields)
            print(output)
            file.write(output)
            file.write('\n')
        file.flush()

        # Application agnostic: one graph with all the values per device
        for key,value in payload_fields.items():
            # Create an entry for each payload field to the same graph
            body['sensors.generic'][device+'_graph_'+key]={'name': device+'_'+key, 'unit': key,'value': float(value),'group': device+'_graph'}

        ###### MODIFY HERE IF YOU WANT CUSTOM PLOTTING
        # Application specific plotting and graphing, customize
        #body['sensors.generic'][device+'_lat']={'name': device+'_lat', 'unit': 'lat','value': float(payload_fields['lat']),'group': 'position'}
        #body['sensors.generic'][device+'_lon']={'name': device+'_lon', 'unit': 'lon','value': float(payload_fields['lon']),'group': 'position'}

        nodewatcher_push(uuid, body, ignore_errors=False)

    except Exception as e:
        print(e)
        pass

def on_publish(mosq, obj, mid):
    print("mid: " + str(mid))

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))

def on_log(mqttc,obj,level,buf):
    print("message:" + str(buf))
    print("userdata:" + str(obj))

mqttc= mqtt.Client()
# Assign event callbacks
mqttc.on_connect=on_connect
mqttc.on_message=on_message

mqttc.username_pw_set(APPID, PSW)
mqttc.connect("eu.thethings.network",1883,60)

# and listen to server
run = True
file = open("mqtt-log.csv", "a")
while run:
    mqttc.loop()
