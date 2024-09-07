
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from api import get_current_user

from models.user import User
from models.device import Device, DeviceToken

router = APIRouter()


class UserRes(BaseModel):
    nickname: str
    phone_number: str


class UserInfo(BaseModel):
    password: Optional[str] = None
    nickname: Optional[str] = None

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
    return {
        'phone_number': user.phone_number,
        'nickname': user.nickname or user.phone_number,
    }


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
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        'phone_number': res_user.phone_number,
        'nickname': res_user.nickname,
    }


class ReqDeviceBinding(BaseModel):
    device_id: str


@router.post('/device/binding')
def device_binding(req: ReqDeviceBinding, user: User = Depends(get_current_user), db = Depends(get_db)):
    """
    绑定设备
    """
    device = Device.get(db, req.device_id)
    if device:
        raise HTTPException(status_code=404, detail="设备已经存在")
    device = user.bind_device(db, req.device_id)
    device_token = DeviceToken.create(db, device.device_id)
    return {
        'device_id': device.device_id,
        'token': device_token.token,
    }


class ReqDeviceUnbinding(BaseModel):
    device_id: str


@router.post('/device/unbinding')
def device_unbinding(req: ReqDeviceBinding, user: User = Depends(get_current_user), db = Depends(get_db)):
    """
    解绑设备，device token 失效
    """
    device = Device.get(db, req.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    user.unbind_device(db, req.device_id)


@router.post('/device/token-gen')
def device_token_gen(req: ReqDeviceBinding, user: User = Depends(get_current_user), db = Depends(get_db)):
    """
    生成设备 token
    """
    device = Device.get(db, req.device_id)
    if not device:
        raise HTTPException(status_code=404, detail="设备不存在")
    if device.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权限操作该设备")
    device_token = DeviceToken.create(db, device.device_id)
    return {
        'device_id': device.device_id,
        'token': device_token.token,
    }


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
        raise HTTPException(status_code=404, detail="设备不存在")
    if device.user_id != user.id:
        raise HTTPException(status_code=403, detail="无权限操作该设备")
    if not device_token:
        raise HTTPException(status_code=404, detail="设备 token 不存在")

    device_token.revoke(db)
