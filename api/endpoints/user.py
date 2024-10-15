
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from api import get_current_user
from api import gen_token, verify_hcaptcha, res_err, res_json, ERRCODES

from models.user import User
from models.device import Device, DeviceToken

router = APIRouter()

class UserResSub(BaseModel):
    email: str
    nickname: str

class UserRes(BaseModel):
    code: int
    message: str
    data: UserResSub | dict


class UserInfo(BaseModel):
    nickname: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:  # 假设我们需要6位数的密码
            raise ValueError('密码长度至少 6 位')
        return v


@router.get('/info')
def user_info(user: User = Depends(get_current_user)) -> UserRes:
    """
    获取用户基础信息
    """
    return res_json({
        'email': user.email,
        'nickname': user.nickname,
    })


@router.post('/info')
def user_info(user_info: UserInfo, user: User = Depends(get_current_user), db = Depends(get_db)) -> UserRes:
    """
    修改用户信息
    """
    password = user_info.password
    nickname = user_info.nickname
    user.update(db, nickname=nickname, password=password)
    if user.phone_number:
        res_user = User.get(db, user.phone_number)
    elif user.email:
        res_user = User.get(db, email=user.email)
    else:
        return res_err(ERRCODES.USER_NOT_FOUND)
    return res_json({
        'phone_number': user.email,
        'nickname': user.nickname,
    })


class ResDeviceSub(BaseModel):
    device_id: str
    device_token: str

class ResDevice(BaseModel):
    code: int
    message: str
    data: ResDeviceSub | dict

class ResUserDevicesSub(BaseModel):
    devices: list[ResDeviceSub]

class ResUserDevices(BaseModel):
    code: int
    message: str
    data: ResUserDevicesSub | dict


@router.get('/devices')
def user_devices(user: User = Depends(get_current_user), db = Depends(get_db)) -> ResUserDevices:
    """
    获取用户绑定的设备
    """
    devices = user.get_devices(db)
    return res_json({
        'devices': [{
            'device_id': device.device_id,
            'device_token': device.get_last_valid_token(db).token if device.get_last_valid_token(db) else '',
        } for device in devices]
    })


class ReqDeviceBinding(BaseModel):
    device_id: str


@router.post('/device/binding')
def device_binding(req: ReqDeviceBinding, user: User = Depends(get_current_user), db = Depends(get_db)) -> ResDevice:
    """
    绑定设备
    """
    if req.device_id == '':
        return res_err(ERRCODES.PARAMS_ERROR)
    device = Device.get(db, req.device_id)
    if device:
        return res_err(ERRCODES.DEVICE_ALREADY_EXISTS)
    device = user.bind_device(db, req.device_id)
    device_token = DeviceToken.create(db, device.device_id)
    return res_json({
        'device_id': device.device_id,
        'device_token': device_token.token,
    })


class ReqDeviceUnbinding(BaseModel):
    device_id: str


@router.post('/device/unbinding')
def device_unbinding(req: ReqDeviceBinding, user: User = Depends(get_current_user), db = Depends(get_db)):
    """
    解绑设备，device token 失效
    """
    device = Device.get(db, req.device_id)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    user.unbind_device(db, req.device_id)
    return res_json()


@router.post('/device/token-gen')
def device_token_gen(req: ReqDeviceBinding, user: User = Depends(get_current_user), db = Depends(get_db)) -> ResDevice:
    """
    生成设备 token
    """
    device = Device.get(db, req.device_id)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    if device.user_id != user.id:
        return res_err(ERRCODES.NO_AUTH_TO_DEVICE)
    device_token = DeviceToken.create(db, device.device_id)
    return res_json({
        'device_id': device.device_id,
        'device_token': device_token.token,
    })


class ReqDeviceTokenRevoke(BaseModel):
    device_id: str
    device_token: str


@router.post('/device/token-revoke')
def device_token_revoke(req: ReqDeviceTokenRevoke, user: User = Depends(get_current_user), db = Depends(get_db)):
    """
    注销设备 token
    """
    device = Device.get(db, req.device_id)
    device_token = DeviceToken.get(db, req.device_id, token=req.device_token)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    if device.user_id != user.id:
        return res_err(ERRCODES.NO_AUTH_TO_DEVICE)
    if not device_token:
        return res_err(ERRCODES.DEVICE_TOKEN_ERROR)

    device_token.revoke(db)
    return res_json()
