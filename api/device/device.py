import asyncio

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from typing import Optional
import queue
import requests
import threading
from time import time
    
from database import get_db
from models.device import Device, DeviceToken
from api import res_json, res_err, ERRCODES, BareRes
from aliyun_services.mqtt import gen_mqtt_token
from aliyun_services.configs import (ALIBABA_CLOUD_ACCESS_KEY_ID,
    MQTT_BROKER_URL, MQTT_INSTANCE_ID, MQTT_GROUP_ID)

router = APIRouter()


class DataAuth(BaseModel):
    status_code: int
    device_id: str
    mqtt_client_id: str
    mqtt_broker_url: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    get_topic: str
    post_topic: str


class ResAuth(BareRes):
    data: DataAuth


class ReqAuth(BaseModel):
    device_id: str
    device_token: str
    firmware_version: Optional[str] = None


@router.post('/firmware/auth_mqtt')
def auth(req_auth: ReqAuth, db = Depends(get_db)) -> ResAuth:
    """
    设备认证
    """
    device = Device.get(db, req_auth.device_id)
    device_token = DeviceToken.get(db, req_auth.device_id, req_auth.device_token)
    firmware_version = req_auth.firmware_version
    if not firmware_version:
        return res_err(ERRCODES.PARAM_ERROR)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    if not device_token or device_token.expired:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)

    client_id=MQTT_GROUP_ID+'@@@'+device.device_id
    topic = 'soundbox'
    userName = 'Token|' + ALIBABA_CLOUD_ACCESS_KEY_ID + '|' + MQTT_INSTANCE_ID
    password = 'RW|' + gen_mqtt_token(topic, device.device_id)
    data = {
        'device_id': device.device_id,
        'mqtt_broker_url': MQTT_BROKER_URL,
        'mqtt_port': 1883,
        'mqtt_username': userName,
        'mqtt_password': password,
        'mqtt_client_id': client_id,
        'get_topic': topic + f'/{device.device_id}/get',
        'post_topic': topic + f'/{device.device_id}/post',
    }
    return res_json(data)


class DataAuthToken(BaseModel):
    mqtt_token: str


class ResAuthToken(BareRes):
    data: DataAuthToken


# @router.post('/firmware/auth_mqtt/token')
# def auth_token(req_auth: ReqAuth, db = Depends(get_db)) -> ResAuthToken:
#     """
#     设备认证
#     """
#     device = Device.get(db, req_auth.device_id)
#     device_token = DeviceToken.get(db, req_auth.device_id, req_auth.device_token)
#     if not device:
#         return res_err(ERRCODES.DEVICE_NOT_FOUND)
#     if not device_token or device_token.expired:
#         return res_err(ERRCODES.DEVICE_TOKEN_ERROR)

#     topic = 'soundbox'
#     data = {
#         'mqtt_token': gen_mqtt_token(topic, device.device_id),
#     }
#     return res_json(data)

# # 发送流式数据到远程服务器的生成器
# def stream_data(data_queue):
#     while True:
#         chunk = data_queue.get()
#         if chunk is None:  # 收集结束标志
#             break
#         yield chunk


# async def async_function(device_id: str, token: str, request: Request, db):
#     body = b''
#     authed = True
#     content_type = request.headers.get('Content-Type')
#     data_queue = queue.Queue()
#     print('111111')

#     def auth():
#         nonlocal authed

#         # device = Device.get(db, device_id)
#         # device_token = DeviceToken.get(db, device_id, token)
#         # print('1')
#         # if not device:
#         #     print('222')
#         #     return False
#         # if not device_token or device_token.expired:
#         #     print('333')
#         #     return False
#         authed = True
#         return authed

#     # def send_stream():
#     #     # 使用流式传输，将队列中的数据发送到服务器
#     #     try:
#     #         response = requests.post(
#     #             'http://example.com/upload',
#     #             data=stream_data(data_queue),  # 使用生成器作为data参数
#     #             headers={'Content-Type': content_type},  # 根据需要调整
#     #             stream=True  # 表明是流式请求
#     #         )
#     #         print(f"Data sent. Response status: {response.status_code}")
#     #     except Exception as e:
#     #         print(f"Error sending data: {e}")

#     # # 启动线程用于发送数据
#     # threading.Thread(target=send_stream, daemon=True).start()


    
#     import time
#     time = int(time.time())
#     with open(f'static/tmp/{time}.opus', 'wb') as f:
#         async for chunk in request.stream():
#             body += chunk
#             if authed:
#                 data_queue.put(chunk)
#                 f.write(body)
#             else:
#                 if not auth():
#                     print('not auth')
#                     return False
#     data_queue.put(None)  # 放入None，表示结束
#     print('full body = ', body)
#     return True


# @router.post('/firmware/audio_upload')
# def audio_upload(request: Request, db = Depends(get_db)) -> BareRes:
#     device_id = request.headers.get('device_id')
#     device_token = request.headers.get('device_token')
#     print('device_id = ', device_id)
#     print('device_token = ', device_token)
#     print('headers = ', request.headers)
#     authed = asyncio.run(async_function(device_id, device_token, request, db))
#     if not authed:
#         return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
#     return res_json()
from aliyun_services.configs import (ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET,
    OSS_BUCKET_NAME, OSS_SERVICE_ENDPOINT)
import requests
import oss2
from datetime import datetime
import msgpack
import json
import hmac
from datetime import datetime
# import time
import base64
import msgpack
from hashlib import sha1
import json
from paho.mqtt.client import MQTT_LOG_INFO, MQTT_LOG_NOTICE, MQTT_LOG_WARNING, MQTT_LOG_ERR, MQTT_LOG_DEBUG
from paho.mqtt.enums import CallbackAPIVersion
import paho.mqtt.client as mqtt
#!/usr/bin/env python
#coding=utf-8
import hmac
from datetime import datetime
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
topic = 'soundbox'
#MQTT 接入点域名，实例初始化之后从控制台获取
brokerUrl="post-cn-lsk3uo7yv02.mqtt.aliyuncs.com"

#MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
client_id=groupId+'@@@'+'server'
#MQTT 接入点域名，实例初始化之后从控制台获取
brokerUrl="post-cn-lsk3uo7yv02.mqtt.aliyuncs.com"
client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id, protocol=mqtt.MQTTv311, clean_session=True)
userName ='Signature'+'|'+ALIBABA_CLOUD_ACCESS_KEY_ID+'|'+instanceId
password = base64.b64encode(hmac.new(ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode(), client_id.encode(), sha1).digest()).decode()
# userName = 'Signature|LTAI5tLQxLqhF7ywAw797nwj|post-cn-lsk3uo7yv02'
# password = 'w8plu9z0LSkl0zzuDJTeVTuI7jM='
client.username_pw_set(userName, password)

    
@router.post("/firmware/audio_upload")
async def create_file(request: Request, db = Depends(get_db)):
    body = b''
    client.connect(brokerUrl)

    # content_type = request.headers.get('Content-Type')
    # data_queue = queue.Queue()
    # device_id = request.headers.get('device_id')
    # device_token = request.headers.get('device_token')
    print('request.headers = ', request.headers)


    # def send_stream():
    #     # 使用流式传输，将队列中的数据发送到服务器
    #     try:
    #         response = requests.post(
    #             'http://example.com/upload',
    #             data=stream_data(data_queue),  # 使用生成器作为data参数
    #             headers={'Content-Type': content_type},  # 根据需要调整
    #             stream=True  # 表明是流式请求
    #         )
    #         print(f"Data sent. Response status: {response.status_code}")
    #     except Exception as e:
    #         print(f"Error sending data: {e}")

    # # 启动线程用于发送数据
    # threading.Thread(target=send_stream, daemon=True).start()
    print('2222 ')

    # data_queue.put(None)  # 放入None，表示结束

    time_str = int(time())
    print('2.5')

    print('444')
    separated = False
    params = b''
    device_id = ''
    device_token = ''
    device = None
    authed = False
    with open(f'/var/www/static.toaitoys.com/{time_str}.opus', 'wb') as f:
        async for chunk in request.stream():
            if not separated:
                i = 0
                while params[-1:] != b"}":
                    params += chunk[i:i+1]
                    i += 1
                    separated = True
                print(params)
                print(i)
                f.write(chunk[i:])
            else:
                f.write(chunk)
            if not authed:
                data = params.decode('utf-8')
                params = json.loads(data)
                device_id = params.get('device_id')
                device_token = params.get('device_token')
                device = Device.get(db, device_id)
                device_token = DeviceToken.get(db, device_id, device_token)
                if not device:
                    return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
                if not device_token or device_token.expired:
                    return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
                authed = True

    print('separated = ', separated)
    NLP_SERVER_URL = 'https://nlp.toaitoys.com/api/SoundBoxPrototype/v1/process_audio'
    API_KEY = '2e5b3768d93c59a68553e2f70d2daa551231a451cbb64d8787a4139df9e8d62a'
    post_data = {
        'device_id': device_id,
        'user_id': device.user_id,
        'oss_link': f'https://static.toaitoys.com/{time_str}.opus',
    }
    print('post_data = ', post_data)
    headers = {
        'X-API-KEY': API_KEY,
    }
    res = requests.post(NLP_SERVER_URL, json=post_data, headers=headers)
    print('res.status_code = ', res.status_code)
    if res.status_code != 200:
        return res_err(ERRCODES.UNKNOWN_ERROR)
    data = res.json()
    print('data = ', data)
    if 'actions' not in data:
        print('nlp err = ', data)
        return
    actions = data['actions']
    print('device_id = ', device_id)
    print('actions = ', actions)

    client.publish(f'soundbox/{device_id}/get', msgpack.packb(actions))
    return res_json()
