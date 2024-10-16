
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from database import get_db
from api import gen_token, verify_hcaptcha, res_err, res_json, ERRCODES, BareRes
from models.user import User, hash_password

from aliyun_services.sms import send_sms, generate_verification_code
from memcached import mc

router = APIRouter()

class ReqRegisterSendCode(BaseModel):
    phone_number: str
    hcaptcha_response: str


@router.post('/register/send_code')
def send_code(req_register_send_code: ReqRegisterSendCode, db = Depends(get_db)) -> BareRes:
    phone_number = req_register_send_code.phone_number
    hcapcha_response = req_register_send_code.hcaptcha_response
    if not verify_hcaptcha(hcapcha_response):
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

class ResToken(BaseModel):
    token: str

class ResRegisterVerifyCode(BareRes):
    data: ResToken


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

    User.create(db, phone_number, username=username, password_hash=hash_password(password))
    mc.delete(phone_number)
    return res_json({'token': gen_token(phone_number)})
