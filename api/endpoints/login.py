
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, field_validator

from api import gen_token
from sms import send_sms, generate_verification_code
from memcached import mc

router = APIRouter()


class Login(BaseModel):
    phone_number: str
    password: str

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

class LoginSendCode(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v


class LoginVerifyCode(BaseModel):
    phone_number: str
    code: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v


@router.post('/')
def login(login: Login):
    """
    手机号和密码登录，会返回 token
    """
    phone_number = login.phone_number
    password = login.password
    print('phone_number:', phone_number)
    print('password:', password)
    # login
    return {
        'token': gen_token()
    }


@router.post('/send-code')
def login_send_code(login_send_code: LoginSendCode):
    """
    手机验证码登录，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = login_send_code.phone_number
    code = login_send_code()
    code = '1212'
    send_sms(phone_number, code)
    mc.set(phone_number, code, time=60)
    return {}


@router.post('/verify-code')
def login_verify_code(login_verify_code: LoginVerifyCode):
    """
    登录，验证验证码。验证成功返回 token
    """
    phone_number = login_verify_code.phone_number
    code = login_verify_code.code
    origin_code = mc.get(phone_number, default='')
    mc.delete(phone_number)

    if origin_code != code:
        raise HTTPException(status_code=404, detail="code error")


    return {
        'token': gen_token()
    }
