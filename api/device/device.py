import asyncio

from fastapi import APIRouter, Depends, Request, Response
from pydantic import BaseModel
from typing import Optional
import queue
import requests
import threading

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


@router.post('/firmware/auth_mqtt/token')
def auth_token(req_auth: ReqAuth, db = Depends(get_db)) -> ResAuthToken:
    """
    设备认证
    """
    device = Device.get(db, req_auth.device_id)
    device_token = DeviceToken.get(db, req_auth.device_id, req_auth.device_token)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    if not device_token or device_token.expired:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)

    topic = 'soundbox'
    data = {
        'mqtt_token': gen_mqtt_token(topic, device.device_id),
    }
    return res_json(data)

# 发送流式数据到远程服务器的生成器
def stream_data(data_queue):
    while True:
        chunk = data_queue.get()
        if chunk is None:  # 收集结束标志
            break
        yield chunk


async def async_function(device_id: str, token: str, request: Request, db):
    body = b''
    authed = True
    content_type = request.headers.get('Content-Type')
    data_queue = queue.Queue()
    print('111111')

    def auth():
        nonlocal authed

        # device = Device.get(db, device_id)
        # device_token = DeviceToken.get(db, device_id, token)
        # print('1')
        # if not device:
        #     print('222')
        #     return False
        # if not device_token or device_token.expired:
        #     print('333')
        #     return False
        authed = True
        return authed

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


    data_queue.put(None)  # 放入None，表示结束
    import time
    time = int(time.time())
    with open(f'static/tmp/{time}.opus', 'wb') as f:
        async for chunk in request.stream():
            body += chunk
            if authed:
                data_queue.put(chunk)
                f.write(body)
            else:
                if not auth():
                    print('not auth')
                    return False
        
    print('full body = ', body)
    return True


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
import time
import msgpack

@router.post("/firmware/audio_upload")
async def create_file(request: Request, db = Depends(get_db)):
    body = b''
    authed = True
    content_type = request.headers.get('Content-Type')
    data_queue = queue.Queue()
    device_id = request.headers.get('device_id')
    device_token = request.headers.get('device_token')
    def auth():
        nonlocal authed
        device = Device.get(db, device_id)
        device_token = DeviceToken.get(db, device_id, device_token)
        print('1')
        if not device:
            print('222')
            return False
        if not device_token or device_token.expired:
            print('333')
            return False
        authed = True
        return authed

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
    print('222 ')
    # async for chunk in request.stream():
    #     body += chunk
    #     print('authed = ', authed)
    #     if authed:
    #         print('chunk = ', chunk)
    #         data_queue.put(chunk)
    #     else:
    #         if not auth():
    #             print('not auth')
    #             return False

    data_queue.put(None)  # 放入None，表示结束
    import time
    time = int(time.time())
    print('333333')
    with open(f'static/tmp/{time}.opus', 'wb') as f:
        async for chunk in request.stream():
            body += chunk
            if authed:
                data_queue.put(chunk)
            else:
                if not auth():
                    print('not auth')
                    return False
        f.write(body)

    # authed = asyncio.run(async_function(device_id, device_token, request, db))
    if not authed:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
    
    NLP_SERVER_URL = 'https://testing.toaitoys.com/api/SoundBoxPrototype/v1/process_audio'
    if device_id in ['00004674224']:
        NLP_SERVER_URL = 'https://nlp.toaitoys.com/api/SoundBoxPrototype/v1/process_audio'
    API_KEY = '2e5b3768d93c59a68553e2f70d2daa551231a451cbb64d8787a4139df9e8d62a'
    # auth = oss2.AuthV2(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
    # bucket = oss2.Bucket(auth, OSS_SERVICE_ENDPOINT, OSS_BUCKET_NAME)
    # oss_link = bucket.sign_url('GET', 'soundbox/'+voice_id, 3600 * 2, slash_safe=True)
    # # print('签名URL的地址为：', oss_link)
    # post_data = {
    #     'device_id': device_id,
    #     'user_id': '12321',
    #     'oss_link': f'http://123.56.219.96:8001/static/tmp/{time}.opus',
    # }
    # headers = {
    #     'X-API-KEY': API_KEY,
    # }
    # res = requests.post(NLP_SERVER_URL, json=post_data, headers=headers)
    # print('res.status_code = ', res.status_code)
    # # data = res.json()
    # print('data = ', data)
    # if 'actions' not in data:
    #     print('nlp err = ', data)
    #     return
    # actions = data['actions']
    # from mqtt.mqtt_listener import client
    # client.publish(f'soundbox/{device_id}/get', msgpack.packb(actions))
    return res_json()


@router.get('/firmware/audio_upload')
def audio_upload(request: Request, db = Depends(get_db)) -> BareRes:
    device_id = request.headers.get('device_id')
    device_token = request.headers.get('device_token')
    authed = asyncio.run(async_function(device_id, device_token, request, db))
    if not authed:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
    return res_json()
