#!/usr/bin/env python
#coding=utf-8
import hmac
from datetime import datetime
import time
import base64
import msgpack
from hashlib import sha1
import json
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.client as mqtt


from models.device import Device
from database import get_db

from .post_handler import request_upload, send_msg, process_nlp

instanceId = "post-cn-lsk3uo7yv02"
ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tLQxLqhF7ywAw797nwj'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = 'XDS3TwzljwoCEdwf6AqkP9GiXe4cY5'
groupId = 'GID_TOAI'

#MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
client_id=groupId+'@@@'+'server'
topic = 'soundbox'
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


def on_message(client, userdata, msg):
    print('in message')
    print('msg.topic: ', msg.topic)
    print('msg.payload: ', str(msg.payload))
    if '/' not in msg.topic:
        print('invalid topic')
        return
    parts = msg.topic.split('/')
    topic, device_id, method = parts[0], parts[1], parts[2]
    if topic != 'soundbox':
        print('invalid topic')
        return

    db_generator = get_db()  # Get the generator object
    db = next(db_generator)  # Start the generator and get the db session

    device = Device.get(db, device_id)
    if not device:
        print('device not found')
        return
    print('method: ', method)
    # 客户端向服务器发送数据
    if method == 'post':
        try:
            body = msgpack.unpackb(msg.payload)
            print('body: ', body)
            command = body.get('command', '')
            if command == 'request_upload':
                time1 = time.time()
                request_upload(client, device_id, topic)
                time2 = time.time()
                print('TIME 后端生成 oss link 时间: ', time2 - time1)
            elif command == 'notify_upload':
                print('notify_upload')
                if 'voice_id' not in body:
                    print('voice_id not found')
                    return
                voice_id = body.get('voice_id', '')
                time1 = time.time()
                process_nlp(client, device_id, topic, device.user_id, voice_id)
                time2 = time.time()
                print('TIME 生成 NLP 参数 + NLP 整个返回时间: ', time2 - time1)
                # TODO nofiy upload to NLP server

            elif command == 'request_update':
                print('request_update')

            elif command == 'online':
                print('device online, device_id: ', device_id)
                send_msg(client, device_id, topic, 'you are online')
            elif command == 'lost':
                print('device offline, device_id: ', device_id)
                send_msg(client, device_id, topic, 'you are lost')

        except Exception as e:
            print('error: ', e)

    # 客户端从服务器获取数据
    elif method == 'get':
        pass

    try:
        # Perform database operations here using `db`
        pass
    finally:
        next(db_generator, None)  # Ensure that the generator finishes and the `finally` block runs


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print('Unexpected disconnection %s' % rc)


client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt.MQTTv311, clean_session=True)

client.on_log = on_log
client.on_connect = on_connect
client.on_message = on_message

userName ='Signature'+'|'+ALIBABA_CLOUD_ACCESS_KEY_ID+'|'+instanceId
password = base64.b64encode(hmac.new(ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode(), client_id.encode(), sha1).digest()).decode()

def mqtt_listener_run():
    client.username_pw_set(userName, password)
    client.connect(brokerUrl)
    client.loop_forever()
