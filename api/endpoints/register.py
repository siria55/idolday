
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from api import gen_token
from models.user import User

from sms import send_sms, generate_verification_code
from memcached import mc

router = APIRouter()


class RegisterSendCode(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v


class RegisterVerifyCode(BaseModel):
    phone_number: str
    code: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v


class ResToken(BaseModel):
    token: str


@router.post('/send-code')
def send_code(register_send_code: RegisterSendCode):
    """
    注册，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = register_send_code.phone_number
    if User.get(phone_number) is not None:
        raise HTTPException(status_code=404, detail="手机号已注册")
    code = generate_verification_code()
    send_sms(phone_number, code)
    mc.set(phone_number, code, time=60 * 10)


@router.post('/verify-code')
def verify_code(register_verify_code: RegisterVerifyCode) -> ResToken:
    """
    注册，验证验证码。验证成功返回 token
    """
    phone_number = register_verify_code.phone_number
    code = register_verify_code.code
    origin_code = mc.get(phone_number, default='')

    if origin_code != code:
        raise HTTPException(status_code=404, detail="验证码错误")
    User.create(phone_number)

    mc.delete(phone_number)
    return {
        'token': gen_token(phone_number)
    }
