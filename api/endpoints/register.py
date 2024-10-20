from typing import Optional

from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, field_validator


from database import get_db
from api import gen_token, captcha_verify_tsec, res_err, res_json, ERRCODES, BareRes, is_valid_password, COOKIE_SECURE
from models.user import User, hash_password

from aliyun_services.sms import send_sms, generate_verification_code
from memcached import mc

router = APIRouter()

class ReqRegisterSendCode(BaseModel):
    phone_number: str
    captcha_ticket: Optional[str] = None
    captcha_randstr: Optional[str] = None


@router.post('/register/send_code')
def send_code(request: Request, req_register_send_code: ReqRegisterSendCode, db = Depends(get_db)) -> BareRes:
    phone_number = req_register_send_code.phone_number
    captcha_ticket = req_register_send_code.captcha_ticket
    captcha_randstr = req_register_send_code.captcha_randstr
    user_ip = request.client.host
    if not captcha_verify_tsec(captcha_ticket, captcha_randstr, user_ip):
        return res_err(ERRCODES.CAPTCHA_ERROR)

    if User.get(db, phone_number=phone_number) is not None:
        return res_err(ERRCODES.PHONE_ALREADY_EXISTS)
    code = generate_verification_code()
    send_sms(phone_number, code)
    mc.set(phone_number, code, time=60 * 10)
    return res_json()


class ReqRegisterVerifyCode(BaseModel):
    phone_number: str
    code: str
    username: str
    password: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v
    
    @field_validator('password')
    def validate_password(cls, v):
        if not is_valid_password(v):
            raise ValueError('密码至少 8 位，包含大小写字母和数字')
        return v


class DataToken(BaseModel):
    token: str

class ResRegisterVerifyCode(BareRes):
    data: DataToken


@router.post('/register/verify_code')
def verify_code(req_register_verify_code: ReqRegisterVerifyCode, db = Depends(get_db)) -> ResRegisterVerifyCode:
    """
    注册，验证验证码。验证成功返回 token
    """
    phone_number = req_register_verify_code.phone_number
    code = req_register_verify_code.code
    username = req_register_verify_code.username
    password = req_register_verify_code.password
    origin_code = mc.get(phone_number, default='')

    if origin_code != code:
        return res_err(ERRCODES.PHONE_VERIFY_CODE_ERROR)
    if User.get(db, username=username) is not None:
        return res_err(ERRCODES.USERNAME_ALREADY_EXISTS)

    user = User.create(db, phone_number, username=username, password_hash=hash_password(password))
    mc.delete(phone_number)
    token = gen_token(user.id)
    content = {
        'token': token,
    }
    res = res_json(content)
    res.set_cookie(key="token", value=token, secure=COOKIE_SECURE, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res