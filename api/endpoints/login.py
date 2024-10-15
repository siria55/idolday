
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, field_validator
from typing import Optional

from database import get_db
from api import gen_token, verify_hcaptcha, captcha_geetest, res_err, res_json, ERRCODES
from models.user import User
from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email
from memcached import mc

router = APIRouter()

class ResToken(BaseModel):
    token: str

class ResTokenBase(BaseModel):
    code: int
    message: str
    data: ResToken | dict

class Login(BaseModel):
    # phone_number: Optional[str] = None
    email: str
    password: str

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


class LoginEmailSendCode(BaseModel):
    email: str
    # hcaptcha_response: Optional[str] = None
    geetest_response: Optional[str] = None

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
def login(login: Login, db = Depends(get_db)) -> ResTokenBase:
    """
    手机号和密码登录，会返回 token
    """
    # phone_number = login.phone_number
    password = login.password
    email = login.email

    user = User.get(db, email=email)
    if not user:
        return res_err(ERRCODES.USER_NOT_FOUND)
    if not user.verify_password(password):
        return res_err(ERRCODES.USER_PASSWORD_ERROR)

    token = gen_token(email)
    res = res_json({'token': token})
    res.set_cookie(key='session', value=token, secure=True, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res


@router.post('/email/send-code')
def login_email_send_code(login_send_code: LoginEmailSendCode):
    """
    邮箱验证码登录，向这个邮箱发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    email = login_send_code.email
    # hcaptcha_response = login_send_code.hcaptcha_response
    geetest_response = login_send_code.geetest_response
    # if not captcha_geetest(geetest_response):
    #     return res_err(ERRCODES.CAPTCHA_GEETEST_ERROR)
    # if not verify_hcaptcha(hcaptcha_response):
    # raise HTTPException(status_code=400, detail="hcaptcha 验证码错误")

    code = generate_verification_code()
    send_email(email, '图爱 - 登录 / 注册验证码', f'您的验证码是：{code}')
    mc.set(email, code, time=60 * 10)
    return res_json()


@router.post('/email/verify-code')
def login_email_verify_code(login_verify_code: LoginEmailVerifyCode, db = Depends(get_db)) -> ResToken:
    """
    登录，验证验证码。如果是新用户会直接创建。验证成功返回 token
    """
    email = login_verify_code.email
    code = login_verify_code.code
    origin_code = mc.get(email, default='')
    if origin_code != code:
        return res_err(ERRCODES.EMAIL_VERIFY_CODE_ERROR)
    if not User.get(db, email=email):
        User.create(db, email=email)
    mc.delete(email)
    token = gen_token(email)
    content = {
        'token': token
    }
    res = res_json(content)
    res.headers['test'] = 'test'
    res.set_cookie(key="session", value=token, secure=True, expires=60 * 60 * 24 * 7 * 30 * 12, samesite='none', httponly=True)
    return res
