from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

from api import get_current_user, decode_token
from models.device import Device
router = APIRouter()

class ResAuth(BaseModel):
    status_code: int
    device_id: str
    mqtt_broker_url: str
    mqtt_username: str
    mqtt_password: str
    c2s_topic: str
    s2c_topic: str
    firmware_version: str


class ReqAuth(BaseModel):
    device_id: str


@router.post('/auth')
def auth(req_auth: ReqAuth) -> ResAuth:
    """
    设备认证
    """
    device = Device.get(req_auth.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")

    data = {
        'status_code': 200,
        'device_id': 'some_random_id',
        'mqtt_broker_url': 'mqtt://broker.emqx.io',
        'mqtt_username': 'emqx',
        'mqtt_password': 'public',
        'c2s_topic': 'c2s',
        's2c_topic': 's2c',
        'firmware_version': '1.0.0',
    }
    return data
