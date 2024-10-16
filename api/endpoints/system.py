
from fastapi import APIRouter

from api import res_json, BareRes, BaseModel


router = APIRouter()


class DataSwitches(BareRes):
    use_captcha: bool

class ResSwitches(BaseModel):
    data: DataSwitches


@router.get('/system/switches')
def switches() -> ResSwitches:
    return res_json({
        'use_captcha': True
    })

class DataUserAvatar(BaseModel):
    url: str


class DataUserAvatars(BaseModel):
    avatars: list[DataUserAvatar]

class ResUserAvatars(BareRes):
    data: DataUserAvatars

@router.get('/system/user_avatars')
def user_avatars() -> ResUserAvatars:
    return res_json([
        {
            'url': 'https://cdn.jsdelivr.net/gh/avataaars/avataaars.svg',
        }
    ])
