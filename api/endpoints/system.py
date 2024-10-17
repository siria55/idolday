
from fastapi import APIRouter

from api import res_json, BareRes, BaseModel, pattern


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

@router.get('/system/user/avatars')
def user_avatars() -> ResUserAvatars:
    return res_json([
        {
            'url': 'https://cdn.jsdelivr.net/gh/avataaars/avataaars.svg',
        }
    ])

class DataPasswordRule(BaseModel):
    pattern: str
    describe: str

class ResPasswordRule(BareRes):
    data: DataPasswordRule


@router.get('/system/user/password_rule')
def password_rule() -> ResPasswordRule:
    return res_json({
        'pattern': pattern,
        'describe': '密码至少 8 位，包含大小写字母和数字',
    })
