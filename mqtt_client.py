#!/usr/bin/env python
#coding=utf-8
import hmac
import base64
from hashlib import sha1
import time
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
from paho.mqtt import client as mqtt
# from paho.mqtt.client import CabackAp
from paho.mqtt.enums import CallbackAPIVersion


def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("your/topic")

def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))

instanceId = "post-cn-lsk3uo7yv02"
ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tLQxLqhF7ywAw797nwj'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = 'XDS3TwzljwoCEdwf6AqkP9GiXe4cY5'
groupId = 'GID_TOAI'

#MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
client_id=groupId+'@@@'+'server'
topic = 'test'
#MQTT 接入点域名，实例初始化之后从控制台获取
brokerUrl="{}.iot-as-mqtt.{}.aliyuncs.com".format(instanceId, 'cn-shanghai')


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
def on_connect(client, userdata, flags, rc):
    print('Connected with result code ' + str(rc))
    client.subscribe(topic, 0)
    for i in range(1, 11):
        print(i)
        rc = client.publish(topic, str(i), qos=0)
        print ('rc: %s' % rc)
        time.sleep(0.1)
def on_message(client, userdata, msg):
    print(msg.topic + ' ' + str(msg.payload))
def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)
client = mqtt.Client(callback_api_version=CallbackAPIVersion.VERSION2, client_id=client_id, protocol=mqtt.MQTTv311, clean_session=True)
client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect
## username和 Password 签名模式下的设置方法，参考文档 https://help.aliyun.com/document_detail/48271.html?spm=a2c4g.11186623.6.553.217831c3BSFry7
userName ='Signature'+'|'+ALIBABA_CLOUD_ACCESS_KEY_ID+'|'+instanceId
password = base64.b64encode(hmac.new(ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode(), client_id.encode(), sha1).digest()).decode()
client.username_pw_set(userName, password)
# ssl设置，并且port=8883
#client.tls_set(ca_certs=None, certfile=None, keyfile=None, cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLS, ciphers=None)
client.connect(brokerUrl, 1883, 60)
client.loop_forever()

# def on_connect(client, userdata, flags, rc):
#     if rc == 0:
#         print("connect success!")
#     else:
#         print("connect failed...  error code is:" + str(rc))
# def connect_mqtt():
#     client.on_connect = on_connect
#     client.connect(brokerUrl, 1883, 60)
#     return client
# def publish_message():
#     # publish 5 messages to pubTopic("/a1LhUsK****/python***/user/update")
#     for i in range(5):
#         message = "ABC" + str(i)
#         client.publish(topic, message)
#         print("publish msg:" + str(i))
#         time.sleep(2)
# publish_message()