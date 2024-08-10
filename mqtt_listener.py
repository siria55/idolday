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
        return
    parts = msg.topic.split('/')
    topic, device_id, method = parts[0], parts[1], parts[2]
    if topic != 'soundbox':
        return

    db_generator = get_db()  # Get the generator object
    db = next(db_generator)  # Start the generator and get the db session

    device = Device.get(db, device_id)
    if not device:
        print('device not found')
        return

    # 客户端向服务器发送数据
    if method == 'post':
        try:
            body = json.loads(msg.payload)
            print('body: ', body)
            command = body.get('command', '')
            if command == 'request_upload':
                # -*- coding: utf-8 -*-
                import oss2
                auth = oss2.AuthV2(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
                bucket = oss2.Bucket(auth, 'https://oss-cn-beijing.aliyuncs.com', 'toai-voice')
                object_name = f'{int(time.time())}.opus'
                path = f'{device_id}/{datetime.now().strftime("%Y%m%d")}'
                voice_id = f'{path}/{object_name}'
                # bucket.put_object(f'soundbox/{path}/', '')

                # 指定Header。
                headers = dict()
                # 指定Content-Type。
                headers['Content-Type'] = 'application/octet-stream'
                # 指定存储类型。
                headers["x-oss-storage-class"] = "Standard"

                # 生成上传文件的签名URL，有效时间为60秒。
                # 生成签名URL时，OSS默认会对Object完整路径中的正斜线（/）进行转义，从而导致生成的签名URL无法直接使用。
                # 设置slash_safe为True，OSS不会对Object完整路径中的正斜线（/）进行转义，此时生成的签名URL可以直接使用。
                url = bucket.sign_url('PUT', 'soundbox/'+voice_id, 6000, slash_safe=True, headers=headers)
                print('签名URL的地址为：', url)
                print('request_upload')
                data = {
                    "command": "request_upload",
                    "upload_url": url,
                    "voice_id": voice_id,
                }
                client.publish(f'{topic}/{device_id}/get', msgpack.packb(data))
                
            elif command == 'nofity_upload':
                print('nofity_upload')
                # TODO nofiy upload to NLP server

                

            elif command == 'request_update':
                print('request_update')
            
            
        except:
            pass

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
