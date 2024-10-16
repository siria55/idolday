
from fastapi import APIRouter, Depends
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from api import get_current_user
from api import res_err, res_json, ERRCODES

from models.user import User

router = APIRouter()

class UserResSub(BaseModel):
    email: str
    username: str

class UserRes(BaseModel):
    code: int
    message: str
    data: UserResSub | dict


class UserInfo(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:  # 假设我们需要6位数的密码
            raise ValueError('密码长度至少 6 位')
        return v


@router.get('/profile')
def user_info(user: User = Depends(get_current_user)) -> UserRes:
    """
    获取用户基础信息
    """
    return res_json({
        'email': user.email,
        'username': user.username,
    })


@router.post('/profile')
def user_info(user_info: UserInfo, user: User = Depends(get_current_user), db = Depends(get_db)) -> UserRes:
    """
    修改用户信息
    """
    password = user_info.password
    username = user_info.username
    user.update(db, username=username, password=password)
    if user.phone_number:
        res_user = User.get(db, user.phone_number)
    elif user.email:
        res_user = User.get(db, email=user.email)
    else:
        return res_err(ERRCODES.USER_NOT_FOUND)
    return res_json({
        'phone_number': user.email,
        'username': user.username,
    })
