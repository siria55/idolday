#!/usr/bin/env python
#coding=utf-8
import hmac
import base64
from hashlib import sha1
import time
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
# from paho.mqtt.client import CabackAp
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.client as mqtt


instanceId = "post-cn-lsk3uo7yv02"
ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tLQxLqhF7ywAw797nwj'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = 'XDS3TwzljwoCEdwf6AqkP9GiXe4cY5'
groupId = 'GID_TOAI'

#MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
client_id=groupId+'@@@'+'server'
topic = 'twowheels'
#MQTT 接入点域名，实例初始化之后从控制台获取
brokerUrl="post-cn-lsk3uo7yv02.mqtt.aliyuncs.com"


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
    client.subscribe(topic + '/#', 0)
    # for i in range(1, 11):
    #     print(i)
    #     rc = client.publish(topic, str(i), qos=0)
    #     print ('rc: %s' % rc)
    #     time.sleep(0.1)


def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt.MQTTv311, clean_session=True)

client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message

userName ='Signature'+'|'+ALIBABA_CLOUD_ACCESS_KEY_ID+'|'+instanceId
password = base64.b64encode(hmac.new(ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode(), client_id.encode(), sha1).digest()).decode()
client.username_pw_set(userName, password)
client.connect(brokerUrl)
client.loop_forever()







