import hmac
import base64
from hashlib import sha1

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from models.device import Device, DeviceToken
from aliyun_services.mqtt import gen_mqtt_token
router = APIRouter()


MQTT_BROKER_URL = 'post-cn-lsk3uo7yv02.mqtt.aliyuncs.com'
instanceId = "post-cn-lsk3uo7yv02"
ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tLQxLqhF7ywAw797nwj'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = 'XDS3TwzljwoCEdwf6AqkP9GiXe4cY5'
groupId = 'GID_TOAI'



class ResAuth(BaseModel):
    status_code: int
    device_id: str
    mqtt_broker_url: str
    mqtt_port: int
    mqtt_username: str
    mqtt_password: str
    get_topic: str
    post_topic: str
    firmware_version: str


class ReqAuth(BaseModel):
    device_id: str
    device_token: str


@router.post('/auth-mqtt')
def auth(req_auth: ReqAuth, db = Depends(get_db)) -> ResAuth:
    """
    设备认证
    """
    device = Device.get(db, req_auth.device_id)
    device_token = DeviceToken.get(db, req_auth.device_id, req_auth.device_token)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    if not device_token or device_token.expired:
        raise HTTPException(status_code=403, detail="设备 token 错误")

    #MQTT ClientID，由 GroupID 和后缀组成，需要保证全局唯一
    client_id=groupId+'@@@'+device.device_id
    topic = 'twowheels'
    # userName ='Signature'+'|'+ALIBABA_CLOUD_ACCESS_KEY_ID+'|'+instanceId
    # password = base64.b64encode(hmac.new(ALIBABA_CLOUD_ACCESS_KEY_SECRET.encode(), client_id.encode(), sha1).digest()).decode()
    userName = 'Token|' + ALIBABA_CLOUD_ACCESS_KEY_ID + '|' + instanceId
    password = 'RW|' + gen_mqtt_token(device.device_id)
    data = {
        'status_code': 200,
        'device_id': device.device_id,
        'mqtt_broker_url': 'MQTT_BROKER_URL',
        'mqtt_port': 1883,
        'mqtt_username': userName,
        'mqtt_password': password,
        'get_topic': topic + f'/{device.device_id}/get',
        'post_topic': topic + f'/{device.device_id}/post',
        'firmware_version': '1.0.0',
    }
    return data
