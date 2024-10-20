
from fastapi import APIRouter, Depends, Request
from pydantic import BaseModel, field_validator
from typing import Optional
from memcached import mc

from database import get_db
from api import res_err, res_json, ERRCODES, get_current_user, is_valid_password, BareRes, BaseModel, captcha_verify_tsec, is_valid_email

from models.user import User
from aliyun_services.sms import send_sms, generate_verification_code
from aliyun_services.email import send_email

router = APIRouter()

class DataUserProfile(BaseModel):
    email: str
    username: str
    phone_number: str
    avatar_url: str

class ResUserProfile(BareRes):
    data: DataUserProfile


@router.get('/profile')
def user_profile(user = Depends(get_current_user)) -> ResUserProfile:
    """
    获取用户基础信息
    """
    return res_json({
        'email': user.email,
        'username': user.username,
        'phone_number': user.phone_number,
        'avatar_url': user.avatar_url,
    })

class UserInfo(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    avatar_name: Optional[str] = None

    @field_validator('password')
    def validate_password(cls, v):
        if is_valid_password(v):
            raise ValueError('密码至少 8 位，包含大小写字母和数字')
        return v


@router.post('/profile')
def user_profile(user_info: UserInfo, user = Depends(get_current_user), db = Depends(get_db)) -> ResUserProfile:
    """
    修改用户信息
    """
    password = user_info.password
    username = user_info.username
    avatar_name = user_info.avatar_name
    if User.get(db, username=username):
        return res_err(ERRCODES.USERNAME_ALREADY_EXISTS)
    if avatar_name not in ['persimmon', 'cactus', 'goat', 'robot']:
        return res_err(ERRCODES.PARAM_ERROR)

    user.update(db, username=username, password=password, avatar_name=avatar_name)
    print('user.phone_number = ', user.phone_number)
    print('type = ', type(user.phone_number))
    updated_user = User.get(db, phone_number=user.phone_number)
    if not updated_user:
        return res_err(ERRCODES.USER_NOT_FOUND)
    return res_json({
        'email': updated_user.email,
        'phone_number': updated_user.phone_number,
        'username': updated_user.username,
        'avatar_url': updated_user.avatar_url,
    })


class ReqProfileSendCode(BaseModel):
    email: Optional[str] = None
    phone_number: Optional[str] = None
    captcha_ticket: str
    captcha_randstr: str

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


@router.post('/profile/send_code')
def profile_send_code(request: Request, req_profile_send_code: ReqProfileSendCode, user: User = Depends(get_current_user), db = Depends(get_db)) -> BareRes:
    """
    初次绑定邮箱 or 换绑手机/邮箱 发验证码
    """
    email = req_profile_send_code.email
    phone_number = req_profile_send_code.phone_number
    captcha_ticket = req_profile_send_code.captcha_ticket
    captcha_randstr = req_profile_send_code.captcha_randstr
    user_ip = request.client.host

    if not captcha_verify_tsec(captcha_ticket, captcha_randstr, user_ip):
        return res_err(ERRCODES.CAPTCHA_ERROR)

    if email and User.get(db, email=email):
        return res_err(ERRCODES.EMAIL_ALREADY_EXISTS)
    elif phone_number and User.get(db, phone_number=phone_number):
        return res_err(ERRCODES.PHONE_ALREADY_EXISTS)

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


class ReqProfileVerifyCode(BaseModel):
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
        if len(v) != 11:
            raise ValueError('请输入正确的手机号')
        return v


@router.post('/profile/verify_code')
def profile_verify_code(
    req_profile_verify_code: ReqProfileVerifyCode,
    user: User = Depends(get_current_user),
    db = Depends(get_db)) -> ResUserProfile:
    """
    验证码验证
    """
    email = req_profile_verify_code.email
    phone_number = req_profile_verify_code.phone_number
    code = req_profile_verify_code.code

    if email:
        if mc.get(email) != code:
            return res_err(ERRCODES.EMAIL_VERIFY_CODE_ERROR)
        user.update(db, email=email)
        mc.delete(email)
    elif phone_number:
        if mc.get(phone_number) != code:
            return res_err(ERRCODES.PHONE_VERIFY_CODE_ERROR)
        user.update(db, phone_number=phone_number)
        mc.delete(phone_number)
    else:
        return res_err(ERRCODES.PARAM_ERROR)

    if user.phone_number:
        updated_user = User.get(db, phone_number=user.phone_number)
    elif user.email:
        updated_user = User.get(db, email=user.email)
    else:
        return res_err(ERRCODES.USER_NOT_FOUND)
    return res_json({
        'email': updated_user.email,
        'phone_number': updated_user.phone_number,
        'username': updated_user.username,
    })
