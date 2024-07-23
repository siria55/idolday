
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, field_validator
from typing import Optional

from api import get_current_user, decode_token
from models import User


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
def user_info(token: str = Depends(get_current_user)) -> UserRes:
    """
    获取用户基础信息
    """
    phone_number = decode_token(token)
    user = User.get(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return {
        'phone_number': user.phone_number,
        'nickname': user.nickname or user.phone_number,
    }


@router.post('/info')
def user_info(user_info: UserInfo, token: str = Depends(get_current_user)) -> UserRes:
    """
    修改用户信息
    """
    password = user_info.password
    nickname = user_info.nickname
    phone_number = decode_token(token)
    user = User.get(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    user.update(nickname=nickname, password_hash=password)
