
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, field_validator

from database import get_db
from api import gen_token
from models.user import User

from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email
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


class RegisterEmailSendCode(BaseModel):
    email: str

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('请输入正确的邮箱')
        return v


class RegisterEmailVerifyCode(BaseModel):
    email: str
    code: str

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('请输入正确的邮箱')
        return v


class ResToken(BaseModel):
    token: str


@router.post('/send-code')
def send_code(register_send_code: RegisterSendCode, db = Depends(get_db)):
    """
    注册，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = register_send_code.phone_number
    if User.get(db, phone_number=phone_number) is not None:
        raise HTTPException(status_code=404, detail="手机号已注册")
    code = generate_verification_code()
    send_sms(phone_number, code)
    mc.set(phone_number, code, time=60 * 10)


@router.post('/verify-code')
def verify_code(register_verify_code: RegisterVerifyCode, db = Depends(get_db)) -> ResToken:
    """
    注册，验证验证码。验证成功返回 token
    """
    phone_number = register_verify_code.phone_number
    code = register_verify_code.code
    origin_code = mc.get(phone_number, default='')

    if origin_code != code:
        raise HTTPException(status_code=404, detail="验证码错误")
    User.create(db, phone_number)

    mc.delete(phone_number)
    return {
        'token': gen_token(phone_number)
    }


@router.post('/email/send-code')
def email_send_code(register_send_code: RegisterSendCode, db = Depends(get_db)):
    """
    注册，向这个邮箱发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    email = register_send_code.email
    if User.get(db, email=email) is not None:
        raise HTTPException(status_code=404, detail="邮箱已注册")
    code = generate_verification_code()
    send_email(email, '图爱-注册验证码', f'您的验证码是：{code}')
    mc.set(email, code, time=60 * 10)


@router.post('/email/verify-code')
def email_verify_code(register_verify_code: RegisterEmailVerifyCode, db = Depends(get_db)) -> ResToken:
    """
    注册，验证验证码。验证成功返回 token
    """
    email = register_verify_code.email
    code = register_verify_code.code
    origin_code = mc.get(email, default='')

    if origin_code != code:
        raise HTTPException(status_code=404, detail="验证码错误")
    User.create(db, email=email)

    mc.delete(email)
    return {
        'token': gen_token(email)
    }
