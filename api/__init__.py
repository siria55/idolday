import jwt
import hmac
import re
import json
import requests
from typing import Optional
from pydantic import BaseModel

from fastapi import HTTPException, Header, Depends, Form, Cookie
from fastapi.responses import JSONResponse

from database import get_db
from models.user import User


HCAPTCHA_SECRET_KEY = 'ES_defd5fe453324be08becb845f6b5cf1f'


class ErrorCodes:
    def __init__(self, file_path=None):
        if file_path:
            self.load_from_file(file_path)

    def load_from_file(self, file_path):
        with open(file_path, 'r') as file:
            data = json.load(file)
            for key, value in data.items():
                setattr(self, key, value)

    def get_message(self, code):
        for key, value in self.__dict__.items():
            if 'code' in value and value['code'] == code:
                return value.get("message", "Unknown error code")
        return "Unknown error code"

ERRCODES = ErrorCodes('return_code.json')


class BareRes(BaseModel):
    code: int
    message: str
    data: dict



def verify_hcaptcha(hcaptcha_response: str = Form(...)):
    data = {
        'secret': HCAPTCHA_SECRET_KEY,
        'response': hcaptcha_response
    }
    response = requests.post('https://hcaptcha.com/siteverify', data=data)
    result = response.json()
    
    if result['success']:
        return True
    else:
        print('captcha err = ', result)
        return False


def is_valid_email(email: str):
    regex = r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w+$'
    if re.match(regex, email):
        return True
    return False


captcha_id = 'b1abf91a4945df22d8221725d3b84fec'
captcha_key = '710d2e50a92de5b7c44c072dd6d09187'
api_server = 'http://gcaptcha4.geetest.com'
def captcha_geetest(params):
    # 2.获取用户验证后前端传过来的验证参数
    if not params:
        return False
    data = json.loads(params)
    lot_number = data.get('lot_number', '')
    captcha_output = data.get('captcha_output', '')
    pass_token = data.get('pass_token', '')
    gen_time = data.get('gen_time', '')
    # 3.生成签名
    # 生成签名使用标准的hmac算法，使用用户当前完成验证的流水号lot_number作为原始消息message，使用客户验证私钥作为key
    # 采用sha256散列算法将message和key进行单向散列生成最终的签名
    lotnumber_bytes = lot_number.encode()
    prikey_bytes = captcha_key.encode()
    sign_token = hmac.new(prikey_bytes, lotnumber_bytes, digestmod='SHA256').hexdigest()
    query = {
        "lot_number": lot_number,
        "captcha_output": captcha_output,
        "pass_token": pass_token,
        "gen_time": gen_time,
        "sign_token": sign_token,
    }
    url = api_server + '/validate' + '?captcha_id={}'.format(captcha_id)
    # 注意处理接口异常情况，当请求极验二次验证接口异常或响应状态非200时做出相应异常处理
    # 保证不会因为接口请求超时或服务未响应而阻碍业务流程
    try:
        res = requests.post(url, query)
        gt_msg = json.loads(res.text)
    except Exception as e:
        print('captcha err = ', gt_msg)
        gt_msg = {'result': 'success', 'reason': 'request geetest api fail'}

    # 5.根据极验返回的用户验证状态, 网站主进行自己的业务逻辑
    if gt_msg['result'] == 'success':
        return True
    else:
        print('captcha err = ', gt_msg)
        return False


def check_session(session: Optional[str] = Cookie(None), db = Depends(get_db)):
    if session is None:
        return res_err(ERRCODES.USER_NOT_FOUND)
    print('session = ', session)
    return session


def get_current_user(Authorization: str = Header(None), session: Optional[str] = Cookie(None), db = Depends(get_db)):  # 使用Header依赖提取token
    if Authorization and Authorization.startswith("Bearer "):
        token = Authorization.split(" ")[1]
    else:
        token = check_session(session, db)

    try:
        phone_number_or_email = decode_token(token)
        print('phone_number_or_email = decode_token(token):', phone_number_or_email)
    except Exception as e:
        return res_err(ERRCODES.USER_NOT_FOUND)
    if not phone_number_or_email:
        return res_err(ERRCODES.USER_NOT_FOUND)

    if '@' in phone_number_or_email:
        user = User.get(db, email=phone_number_or_email)
    else:
        user = User.get(db, phone_number=phone_number_or_email)
    if not user:
        return res_err(ERRCODES.USER_NOT_FOUND)
    print('user 111 email = ', user.email)
    return user  # 实际场景中这里可能返回解析token得到的用户信息


def gen_token(phone_number_or_email):
    print(' gen token phone_number_or_email:', phone_number_or_email)
    encoded_jwt = jwt.encode({"phone_number_or_email": phone_number_or_email}, "secret", algorithm="HS256")
    return encoded_jwt


def decode_token(token):
    return jwt.decode(token, "secret", algorithms=["HS256"]).get('phone_number_or_email')


def res_err(err_codes):
    res = {
        'code': err_codes.get('code', 0),
        'message': err_codes.get('message', 'success'),
        'data': {}
    }
    return JSONResponse(status_code=200, content=res)

def res_json(data={}):
    res = {
        'code': 0,
        'message': 'success',
        'data': data
    }
    return JSONResponse(status_code=200, content=res)

# 必须包含大小写字母和数字，长度>=8
pattern = r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[a-zA-Z\d]{8,}$'
def is_valid_password(password: str):
    if re.match(pattern, password):
        return True
    return False
