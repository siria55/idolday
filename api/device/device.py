import asyncio

from fastapi import APIRouter, Depends, Request
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
    authed = False
    content_type = request.headers.get('Content-Type')
    data_queue = queue.Queue()

    def auth():
        nonlocal authed

        device = Device.get(db, device_id)
        device_token = DeviceToken.get(db, device_id, token)
        if not device:
            return False
        if not device_token or device_token.expired:
            return False
        authed = True

    def send_stream():
        # 使用流式传输，将队列中的数据发送到服务器
        try:
            response = requests.post(
                'http://example.com/upload', 
                data=stream_data(data_queue),  # 使用生成器作为data参数
                headers={'Content-Type': 'application/octet-stream'},  # 根据需要调整
                stream=True  # 表明是流式请求
            )
            print(f"Data sent. Response status: {response.status_code}")
        except Exception as e:
            print(f"Error sending data: {e}")

    # 启动线程用于发送数据
    threading.Thread(target=send_stream, daemon=True).start()

    async for chunk in request.stream():
        body += chunk
        if authed:
            data_queue.put(chunk)
        else:
            if not auth():
                print('not auth')
                return False

    data_queue.put(None)  # 放入None，表示结束
    print('full body = ', body)


@router.post('/audio_upload')
def audio_upload(device_id: str, device_token: str, request: Request, db = Depends(get_db)) -> BareRes:
    authed = asyncio.run(async_function(device_id, device_token, request, db))  # 在同步函数中运行异步函数
    if not authed:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
    return res_json()
