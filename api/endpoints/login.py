
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from api import gen_token
from models import User
from sms import send_sms, generate_verification_code
from memcached import mc

router = APIRouter()

class ResToken(BaseModel):
    token: str


class Login(BaseModel):
    phone_number: str
    password: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少 6 位')
        return v

class LoginSendCode(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v


class LoginVerifyCode(BaseModel):
    phone_number: str
    code: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v


@router.post('/')
def login(login: Login) -> ResToken:
    """
    手机号和密码登录，会返回 token
    """
    phone_number = login.phone_number
    password = login.password
    user = User.get(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.verify_password(password):
        raise HTTPException(status_code=400, detail="密码错误")
    return {
        'token': gen_token(phone_number)
    }


@router.post('/send-code')
def login_send_code(login_send_code: LoginSendCode):
    """
    手机验证码登录，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = login_send_code.phone_number
    code = generate_verification_code()
    send_sms(phone_number, code)
    mc.set(phone_number, code, time=60 * 10)


@router.post('/verify-code')
def login_verify_code(login_verify_code: LoginVerifyCode) -> ResToken:
    """
    登录，验证验证码。验证成功返回 token
    """
    phone_number = login_verify_code.phone_number
    code = login_verify_code.code
    origin_code = mc.get(phone_number, default='')
    print(f'origin_code = {origin_code}')
    if origin_code != code:
        raise HTTPException(status_code=400, detail="验证码错误")
    mc.delete(phone_number)
    return {
        'token': gen_token(phone_number)
    }
