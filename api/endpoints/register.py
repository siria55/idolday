
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from sms import send_sms, generate_verification_code
from memcached import mc

router = APIRouter()


class RegisterSendCode(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v


class RegisterVerifyCode(BaseModel):
    phone_number: str
    code: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v


@router.post('/send-code')
def send_code(register_send_code: RegisterSendCode):
    """
    注册，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = register_send_code.phone_number
    code = generate_verification_code()
    code = '1212'
    send_sms(phone_number, code)
    mc.set(phone_number, code, time=60)
    return {}


@router.post('/verify-code')
def verify_code(register_verify_code: RegisterVerifyCode):
    """
    注册，验证验证码。验证成功返回 token
    """
    phone_number = register_verify_code.phone_number
    code = register_verify_code.code
    origin_code = mc.get(phone_number, default='')
    mc.delete(phone_number)

    if origin_code != code:
        raise HTTPException(status_code=404, detail="code error")

    #TODO 创建用户

    return {
        'token': '112312323231231232frfr'
    }
