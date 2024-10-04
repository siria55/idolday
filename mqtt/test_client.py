#!/usr/bin/env python
#coding=utf-8

import requests


from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
import paho.mqtt.client as mqtt
import msgpack
from .post_handler import send_msg

# 定义回调函数
def on_log(client, userdata, level, buf):
    if level == MQTT_LOG_INFO:
        head = 'INFO'
    elif level == MQTT_LOG_NOTICE:
        head = 'NOTICE'
    elif level == MQTT_LOG_WARNING:
        head = 'WARN'
    elif level == MQTT_LOG_ERR:
        head = 'ERR'
    elif level == MQTT_LOG_DEBUG:
        head = 'DEBUG'
    else:
        head = level
    print('%s: %s' % (head, buf))


def on_connect(client, userdata, flags, rc, ps):

    print('Connected with result code ' + str(rc))
    print('flags = %s' % flags)
    print('userdata = %s' % userdata)
    client.subscribe('soundbox/0000aaaa/get', 0)
    # client.publish('soundbox/0000aaaa/post', msgpack.packb({"command": "notify_upload", "voice_id": "hhh/20240906/1725557132.opus"}))
    # client.publish('soundbox/0000aaaa/post', msgpack.packb({"command": "notify_upload"}))
    
    # for i in range(1, 11):
    #     print(i)
    #     rc = client.publish(topic, str(i), qos=0)
    #     print ('rc: %s' % rc)
    #     time.sleep(0.1)


def on_message(client, userdata, msg):
    print('msg.payload: ', str(msg.payload))
    data = msgpack.unpackb(msg.payload)
    print(msg.topic + ' ' + str(data))


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)


def get_mq_client():
    url = 'http://localhost:8000/api/v1/devices/auth-mqtt'
    data = {
        'device_id': '0000aaaa',
        'device_token': 'f49d84309c43a2d3310208a2388fa4ce'
    }
    res = requests.post(url, json=data)
    res_data = res.json()
    mqtt_broker_url = res_data['mqtt_broker_url']
    mqtt_username = res_data['mqtt_username']
    mqtt_password = res_data['mqtt_password']
    mqtt_port = res_data['mqtt_port']
    mqtt_client_id = res_data['mqtt_client_id']
    get_topic = res_data['get_topic']
    post_topic = res_data['post_topic']
    device_id = res_data['device_id']
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, mqtt_client_id, protocol=mqtt.MQTTv311, clean_session=True)
    client.on_log = on_log
    client.on_connect = on_connect
    client.on_message = on_message
    client.username_pw_set(mqtt_username, mqtt_password)
    client.connect(mqtt_broker_url)
    # client.loop_forever()
    return client

# for test
client_id='GID_TOAI@@@server_test'
brokerUrl="post-cn-lsk3uo7yv02.mqtt.aliyuncs.com"

def send_to_client():
    device_id = '00004674224'
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt.MQTTv311, clean_session=True)

    userName = 'Signature|LTAI5tLQxLqhF7ywAw797nwj|post-cn-lsk3uo7yv02'
    password = 'w8plu9z0LSkl0zzuDJTeVTuI7jM='

    client.username_pw_set(userName, password)
    client.connect(brokerUrl)
    # topic = 'soundbox/' + device_id + '/post'
    # client.loop_forever()
    # send_msg(client, device_id, topic, 'you are lost')
    sleep_command = {'action': 'combine',
        'command': 'action',
        'value': [{'action': 'sleep', 'sleep_ms': 0, 'time': 0, 'wait_event': []}]}
    wifi_command = {}
    client.publish(f'soundbox/{device_id}/get', msgpack.packb(sleep_command))
