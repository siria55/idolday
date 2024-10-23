import jwt
import hmac
import re
import os
import json
import requests

from pydantic import BaseModel
from fastapi import Form
from fastapi.responses import JSONResponse

from database import get_db

from tencentcloud.common.common_client import CommonClient
from tencentcloud.common import credential
from tencentcloud.common.exception.tencent_cloud_sdk_exception import TencentCloudSDKException
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile


HCAPTCHA_SECRET_KEY = 'ES_defd5fe453324be08becb845f6b5cf1f'
COOKIE_SECURE = False

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

def build_static_avatars():
    avatars = os.listdir('static/avatar')
    return avatars
STATIC_AVATARS = build_static_avatars()


def verify_hcaptcha(hcaptcha_response: str = Form(...)):
    return True
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

SECRET_ID_TENCENT = 'AKIDcAh19556vZNOTUMFF8oFVWddVFoBORNA'
SECRET_KEY_TENCENT = 'stv7iBTZU5byQURDrQ5h9OQK6e5UtOOW'
def captcha_verify_tsec(captcha_ticket: str, captcha_randstr: str, user_ip: str):
    try:
        # 实例化一个认证对象，入参需要传入腾讯云账户 SecretId 和 SecretKey，此处还需注意密钥对的保密
        # 代码泄露可能会导致 SecretId 和 SecretKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考，建议采用更安全的方式来使用密钥，请参见：https://cloud.tencent.com/document/product/1278/85305
        # 密钥可前往官网控制台 https://console.cloud.tencent.com/cam/capi 进行获取
        cred = credential.Credential(SECRET_ID_TENCENT, SECRET_KEY_TENCENT)

        httpProfile = HttpProfile()
        httpProfile.endpoint = "captcha.tencentcloudapi.com"
        clientProfile = ClientProfile()
        clientProfile.httpProfile = httpProfile

        params = {
            'CaptchaType': 9,
            'Ticket': captcha_ticket,
            'UserIp': user_ip,
            'Randstr': captcha_randstr,
            'CaptchaAppId': 190256550,
            'AppSecretKey': 'rofZxqPSFmofSEBa4wGflMVrc'
        }
        common_client = CommonClient("captcha", "2019-07-22", cred, "", profile=clientProfile)
        res = common_client.call_json("DescribeCaptchaResult", params)
        print('captcha res = ', res)
        data = res.get('Response', {})
        captcha_code = data.get('CaptchaCode', 0)
        if captcha_code == 1:
            return True
        return False
    except TencentCloudSDKException as err:
        print('tencent captcha err = ', err)
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



# def get_current_user(Authorization: str = Header(None), token: Optional[str] = Cookie(None), db = Depends(get_db)) -> User:
#     print('tokentoken = ', token)
#     if Authorization and Authorization.startswith("Bearer "):
#         res_token = Authorization.split(" ")[1]
#     elif token:
#         res_token = token
#     else:
#         raise HTTPException(status_code=401)

#     try:
#         user_id = decode_token(res_token)
#         print('user_id = ', user_id)
#         user = User.get(db, id=user_id)
#         print('user = ', user)
#     except Exception as e:
#         raise HTTPException(status_code=401)
#     if not user:
#         raise HTTPException(status_code=401)
#     return user


def gen_token(user_id):
    encoded_jwt = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")
    return encoded_jwt


def decode_token(token):
    return jwt.decode(token, "secret", algorithms=["HS256"]).get('user_id')


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
