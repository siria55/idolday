import hmac
import base64
from hashlib import sha1
import asyncio

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from models.device import Device, DeviceToken
from api import res_json, res_err, ERRCODES
from aliyun_services.mqtt import gen_mqtt_token
from aliyun_services.configs import (ALIBABA_CLOUD_ACCESS_KEY_ID,
    MQTT_BROKER_URL, MQTT_INSTANCE_ID, MQTT_GROUP_ID)

router = APIRouter()


class ResAuth(BaseModel):
    status_code: int
    device_id: str
    mqtt_client_id: str
    mqtt_broker_url: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    get_topic: str
    post_topic: str


class ResAuthToken(BaseModel):
    mqtt_token: str


class ReqAuth(BaseModel):
    device_id: str
    device_token: str
    firmware_version: Optional[str] = None


@router.post('/auth-mqtt')
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


@router.post('/auth-mqtt/token')
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


async def async_function(device_id: str, token: str, request: Request, db):
    body = b''
    authed = False

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
        nonlocal body
        print('body = ', body)

    async for chunk in request.stream():
        body += chunk
        if authed:
            send_stream()
        else:
            if not auth():
                print('not auth')
                return False


@router.post('/audio_upload')
def audio_upload(device_id: str, device_token: str, request: Request, db = Depends(get_db)):
    authed = asyncio.run(async_function(device_id, device_token, request, db))  # 在同步函数中运行异步函数
    if not authed:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)
    return res_json()
