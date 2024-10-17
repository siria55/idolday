
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from database import get_db
from api import get_current_user, BareRes
from api import res_err, res_json, ERRCODES

from models.user import User
from models.device import Device, DeviceToken

router = APIRouter()

class DataDevice(BaseModel):
    device_id: str
    device_token: str

class DataDeviceList(BaseModel):
    devices: list[DataDevice]

class ResUserDevices(BareRes):
    data: DataDeviceList


@router.get('/devices')
def user_devices(current_user: User = Depends(get_current_user), db = Depends(get_db)) -> ResUserDevices:
    """
    获取用户绑定的设备
    """
    devices = current_user.get_devices(db)
    return res_json({
        'devices': [{
            'device_id': device.device_id,
            'device_token': device.get_last_valid_token(db).token if device.get_last_valid_token(db) else '',
        } for device in devices]
    })


class ResDevice(BareRes):
    data: DataDevice


@router.post('/devices/{device_id}')
def device_binding(device_id: str, current_user: User = Depends(get_current_user), db = Depends(get_db)) -> ResDevice:
    """
    绑定设备
    """
    if device_id == '':
        return res_err(ERRCODES.PARAMS_ERROR)
    device = Device.get(db, device_id)
    if device:
        return res_err(ERRCODES.DEVICE_ALREADY_EXISTS)
    device = current_user.bind_device(db, device_id)
    device_token = DeviceToken.create(db, device.device_id)
    return res_json({
        'device_id': device.device_id,
        'device_token': device_token.token,
    })


class ReqDeviceUnbinding(BaseModel):
    device_id: str


@router.delete('/devices/{device_id}')
def device_unbinding(device_id: str, current_user: User = Depends(get_current_user), db = Depends(get_db)) -> BareRes:
    """
    解绑设备，同时删除 device_token
    """
    device = Device.get(db, device_id)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    if device.user_id != current_user.id:
        return res_err(ERRCODES.NO_AUTH_TO_DEVICE)
    current_user.unbind_device(db, device_id)
    return res_json()


@router.post('/devices/{device_id}/token')
def device_token_gen(device_id: str, current_user: User = Depends(get_current_user), db = Depends(get_db)) -> ResDevice:
    """
    生成设备 token
    """
    device = Device.get(db, device_id)
    if not device:
        return res_err(ERRCODES.DEVICE_NOT_FOUND)
    if device.user_id != current_user.id:
        return res_err(ERRCODES.NO_AUTH_TO_DEVICE)
    device.remove_tokens(db)
    device_token = DeviceToken.create(db, device.device_id)
    return res_json({
        'device_id': device.device_id,
        'device_token': device_token.token,
    })
