
from fastapi import APIRouter, Depends, Request
from pydantic import field_validator, BaseModel
from typing import Optional

from database import get_db
from api import gen_token, captcha_verify_tsec, res_err, res_json, ERRCODES, is_valid_email, BareRes, is_valid_password, COOKIE_SECURE
from models.user import User
from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email
from memcached import mc

router = APIRouter()


class DataToken(BaseModel):
    token: str

class ResLogin(BareRes):
    data: DataToken


class ReqLogin(BaseModel):
    login_input: str
    password: str
    captcha_ticket: str
    captcha_randstr: str

    @field_validator('password')
    def validate_password(cls, v):
        if not is_valid_password(v):
            raise ValueError('密码至少 8 位，包含大小写字母和数字')
        return v


@router.post('/login')
def login(request: Request, req_login: ReqLogin, db = Depends(get_db)) -> ResLogin:
    """
    username/email/phone_number 三选一 + 密码 登录，会返回 token
    """
    login_input = req_login.login_input
    password = req_login.password
    captcha_ticket = req_login.captcha_ticket
    captcha_randstr = req_login.captcha_randstr
    user_ip = request.client.host
    print('user_ip = ', user_ip)
    if not captcha_verify_tsec(captcha_ticket, captcha_randstr, user_ip):
        return res_err(ERRCODES.CAPTCHA_ERROR)
    
    user = User.get(db, username=login_input)
    if not user:
        user = User.get(db, email=login_input)
    if not user:
        user = User.get(db, phone_number=login_input)
    if not user:
        return res_err(ERRCODES.USER_NOT_FOUND)

    if not user.verify_password(password):
        return res_err(ERRCODES.USER_PASSWORD_ERROR)

    token = gen_token(user.id)
    res = res_json({
        'token': token,
    })
    res.set_cookie(key='token', value=token, secure=COOKIE_SECURE, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res


class ReqLoginSendCode(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    captcha_ticket: Optional[str] = None
    captcha_randstr: Optional[str] = None

    @field_validator('email')
    def validate_email(cls, v):
        if not is_valid_email(v):
            raise ValueError('请输入正确的邮箱')
        return v


@router.post('/login/send_code')
def login_send_code(request: Request, req_login_send_code: ReqLoginSendCode, db = Depends(get_db)) -> BareRes:
    email = req_login_send_code.email
    phone_number = req_login_send_code.phone_number
    captcha_ticket = req_login_send_code.captcha_ticket
    captcha_randstr = req_login_send_code.captcha_randstr
    user_ip = request.client.host

    if not captcha_verify_tsec(captcha_ticket, captcha_randstr, user_ip):
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
        user = User.get(db, email=email)
        if not user:
            return res_err(ERRCODES.USER_NOT_FOUND)

        mc.delete(email)
        token = gen_token(user.id)
    elif phone_number:
        origin_code = mc.get(phone_number, default='')
        if origin_code != code:
            return res_err(ERRCODES.PHONE_VERIFY_CODE_ERROR)
        user = User.get(db, phone_number=phone_number)
        if not user:
            return res_err(ERRCODES.USER_NOT_FOUND)

        mc.delete(phone_number)
        token = gen_token(user.id)
    else:
        return res_err(ERRCODES.PARAM_ERROR)

    content = {
        'token': token,
    }
    res = res_json(content)
    res.set_cookie(key="token", value=token, secure=COOKIE_SECURE, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res
