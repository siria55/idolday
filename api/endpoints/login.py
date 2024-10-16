
from fastapi import APIRouter, Depends
from pydantic import field_validator, BaseModel
from typing import Optional

from database import get_db
from api import gen_token, verify_hcaptcha, res_err, res_json, ERRCODES, is_valid_email, BareRes
from models.user import User
from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email
from memcached import mc

router = APIRouter()


class ResToken(BaseModel):
    token: str

class ResLogin(BareRes):
    data: ResToken


class ReqLogin(BaseModel):
    phone_number: Optional[str] = None
    email: Optional[str] = None
    username: Optional[str] = None
    password: str

    @field_validator('email')
    def validate_email(cls, v):
        if not is_valid_email(v):
            raise ValueError('请输入正确的邮箱')
        return v

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        # TODO 密码强度检验
        if len(v) < 6:
            raise ValueError('密码至少 6 位')
        return v


@router.post('/login')
def login(req_login: ReqLogin, db = Depends(get_db)) -> ResLogin:
    """
    username/email/phone_number 三选一 + 密码 登录，会返回 token
    """
    phone_number = req_login.phone_number
    email = req_login.email
    username = req_login.username
    password = req_login.password

    if email:
        user = User.get(db, email=email)
    elif phone_number:
        user = User.get(db, phone_number=phone_number)
    elif username:
        user = User.get(db, username=username)
    else:
        return res_err(ERRCODES.PARAM_ERROR)
    if not user:
        return res_err(ERRCODES.USER_NOT_FOUND)
    if not user.verify_password(password):
        return res_err(ERRCODES.USER_PASSWORD_ERROR)

    token = gen_token(email)
    res = res_json({'token': token})
    res.set_cookie(key='session', value=token, secure=True, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res


class ReqLoginSendCode(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    hcaptcha_response: Optional[str] = None

    @field_validator('email')
    def validate_email(cls, v):
        if not is_valid_email(v):
            raise ValueError('请输入正确的邮箱')
        return v


@router.post('/login/send_code')
def login_send_code(req_login_send_code: ReqLoginSendCode, db = Depends(get_db)) -> BareRes:
    email = req_login_send_code.email
    phone_number = req_login_send_code.phone_number
    hcaptcha_response = req_login_send_code.hcaptcha_response

    if not verify_hcaptcha(hcaptcha_response):
        return res_err(ERRCODES.CAPTCHA_ERROR)
    
    if email and not User.get(db, email=email):
        return res_err(ERRCODES.USER_NOT_FOUND)
    elif phone_number and not User.get(db, phone_number=phone_number):
        return res_err(ERRCODES.USER_NOT_FOUND)

    code = generate_verification_code()
    if email:
        send_email(email, '图爱 - 登录', f'您的验证码是：{code}')
        mc.set(email, code, time=60 * 10)
    elif phone_number:
        send_sms(phone_number, code)
        mc.set(phone_number, code, time=60 * 10)
    else:
        return res_err(ERRCODES.PARAM_ERROR)
    return res_json()


class ReqLoginVerifyCode(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    code: str

    @field_validator('email')
    def validate_email(cls, v):
        if not is_valid_email(v):
            raise ValueError('请输入正确的邮箱')
        return v

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        # TODO 抽象 手机号验证
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v


@router.post('/login/verify_code')
def login_verify_code(login_verify_code: ReqLoginVerifyCode, db = Depends(get_db)) -> ResLogin:
    email = login_verify_code.email
    phone_number = login_verify_code.phone_number
    code = login_verify_code.code

    if email:
        origin_code = mc.get(email, default='')
        if origin_code != code:
            return res_err(ERRCODES.EMAIL_VERIFY_CODE_ERROR)
        if not User.get(db, email=email):
            return res_err(ERRCODES.USER_NOT_FOUND)

        mc.delete(email)
        token = gen_token(email)
    elif phone_number:
        origin_code = mc.get(phone_number, default='')
        if origin_code != code:
            return res_err(ERRCODES.PHONE_VERIFY_CODE_ERROR)
        if not User.get(db, phone_number=phone_number):
            return res_err(ERRCODES.USER_NOT_FOUND)

        mc.delete(phone_number)
        token = gen_token(phone_number)
    else:
        return res_err(ERRCODES.PARAM_ERROR)

    content = {
        'token': token
    }
    res = res_json(content)
    res.set_cookie(key="session", value=token, secure=True, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res
