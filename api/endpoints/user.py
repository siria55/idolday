
from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator

from api import get_current_user


router = APIRouter()


class User(BaseModel):
    nickname: str
    phone_number: str


class UserInfo(BaseModel):
    phone_number: str
    password: str
    nickname: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:  # 假设我们需要6位数的密码
            raise ValueError('Password must be at least 6 digits')
        return v


@router.get('/info')
def user_info(token: str = Depends(get_current_user)) -> User:
    """
    获取用户基础信息
    """
    return {
        'phone_number': '12312312311',
        'nickname': 'wwwsss',
    }


@router.post('/info')
def user_info(user_info: UserInfo, token: str = Depends(get_current_user)) -> User:
    """
    修改用户信息
    """
    phone_number = user_info.phone_number
    password = user_info.password
    nickname = user_info.nickname
    print('phone_number:', phone_number)
    print('password:', password)
    print('nickname:', nickname)
    # complete register
    return {
        'phone_number': '12312312311',
        'nickname': 'wwwsss',
    }
