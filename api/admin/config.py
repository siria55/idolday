import hmac
import base64
from hashlib import sha1

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from models.device import Device, DeviceToken
from aliyun_services.mqtt import gen_mqtt_token
from aliyun_services.configs import (ALIBABA_CLOUD_ACCESS_KEY_ID,
    MQTT_BROKER_URL, MQTT_INSTANCE_ID, MQTT_GROUP_ID)
router = APIRouter()

@router.get('/system-config')
def system_config():
    """
    获取系统配置
    """
    return {
        'use_captcha': True,
    }
