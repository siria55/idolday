
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from api import gen_token, verify_hcaptcha
from models.user import User
from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email
from memcached import mc

router = APIRouter()


class ResToken(BaseModel):
    token: str


class Login(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    password: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('请输入正确的邮箱')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError('密码至少 6 位')
        return v

class LoginSendCode(BaseModel):
    phone_number: str
    hcaptcha_response: Optional[str] = None

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


class LoginEmailSendCode(BaseModel):
    email: str
    hcaptcha_response: Optional[str] = None

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('请输入正确的邮箱')
        return v


class LoginEmailVerifyCode(BaseModel):
    email: str
    code: str

    @field_validator('email')
    def validate_email(cls, v):
        if '@' not in v:
            raise ValueError('请输入正确的邮箱')
        return v


@router.post('/')
def login(login: Login, db = Depends(get_db)) -> ResToken:
    """
    手机号和密码登录，会返回 token
    """
    phone_number = login.phone_number
    password = login.password
    email = login.email
    if phone_number:
        user = User.get(db, phone_number)
    elif email:
        user = User.get(db, email=email)
    else:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if not user.verify_password(password):
        raise HTTPException(status_code=400, detail="密码错误")

    token = gen_token(phone_number or email)
    content = {
        'token': token
    }
    response = JSONResponse(content=content)
    response.set_cookie(key='session', value=token, secure=True, expires=60 * 60 * 24 * 7 * 30 * 12)
    return response


# @router.post('/send-code')
# def login_send_code(login_send_code: LoginSendCode):
#     """
#     手机验证码登录，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
#     """
#     phone_number = login_send_code.phone_number
#     hcaptcha_response = login_send_code.hcaptcha_response
#     if not verify_hcaptcha(hcaptcha_response):
#         raise HTTPException(status_code=400, detail="hcaptcha 验证码错误")
#     code = generate_verification_code()
#     send_sms(phone_number, code)
#     mc.set(phone_number, code, time=60 * 10)


# @router.post('/verify-code')
# def login_verify_code(login_verify_code: LoginVerifyCode,  db = Depends(get_db)) -> ResToken:
#     """
#     登录，验证验证码。如果是新用户会直接创建。验证成功返回 token
#     """
#     phone_number = login_verify_code.phone_number
#     code = login_verify_code.code
#     origin_code = mc.get(phone_number, default='')
#     print(f'origin_code = {origin_code}')
#     if origin_code != code:
#         raise HTTPException(status_code=400, detail="验证码错误")
#     if not User.get(db, phone_number=phone_number):
#         User.create(db, phone_number)
#     mc.delete(phone_number)
#     return {
#         'token': gen_token(phone_number)
#     }


@router.post('/email/send-code')
def login_email_send_code(login_send_code: LoginEmailSendCode):
    """
    邮箱验证码登录，向这个邮箱发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    email = login_send_code.email
    hcaptcha_response = login_send_code.hcaptcha_response
    if not verify_hcaptcha(hcaptcha_response):
        raise HTTPException(status_code=400, detail="hcaptcha 验证码错误")

    code = generate_verification_code()
    send_email(email, '图爱 - 登录 / 注册验证码', f'您的验证码是：{code}')
    mc.set(email, code, time=60 * 10)


@router.post('/email/verify-code')
def login_email_verify_code(login_verify_code: LoginEmailVerifyCode, db = Depends(get_db)) -> ResToken:
    """
    登录，验证验证码。如果是新用户会直接创建。验证成功返回 token
    """
    email = login_verify_code.email
    code = login_verify_code.code
    origin_code = mc.get(email, default='')
    if origin_code != code:
        raise HTTPException(status_code=400, detail="验证码错误")
    if not User.get(db, email=email):
        User.create(db, email=email)
    mc.delete(email)
    token = gen_token(email)
    content = {
        'token': token
    }
    response = JSONResponse(content=content)
    response.headers['test'] = 'test'
    response.set_cookie(key="session", value=token, secure=True, expires=60 * 60 * 24 * 7 * 30 * 12)
    return response
