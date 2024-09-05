#!/usr/bin/env python
#coding=utf-8

import requests


from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
import paho.mqtt.client as mqtt
import msgpack

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
    client.subscribe('soundbox/hhh/get', 0)
    # client.publish('soundbox/hhh/post', msgpack.packb({"command": "nofity_upload", "voice_id": "hhh/20240906/1725557132.opus"}))
    # client.publish('soundbox/hhh/post', msgpack.packb({"command": "nofity_upload"}))
    
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
        'device_id': 'hhh',
        'device_token': 'f8e930f261602b52cea21897306bc88f'
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
    
    
