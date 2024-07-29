import os
import sys
import time
from datetime import datetime
import uuid
import hmac
import hashlib
import base64
from typing import List
import random
from urllib import parse
import requests

from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tLQxLqhF7ywAw797nwj'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = 'XDS3TwzljwoCEdwf6AqkP9GiXe4cY5'


class AccessToken:
    @staticmethod
    def _encode_text(text):
        encoded_text = parse.quote_plus(text)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
    @staticmethod
    def _encode_dict(dic):
        keys = dic.keys()
        dic_sorted = [(key, dic[key]) for key in sorted(keys)]
        encoded_text = parse.urlencode(dic_sorted)
        return encoded_text.replace('+', '%20').replace('*', '%2A').replace('%7E', '~')
    @staticmethod
    def create_token(access_key_id, access_key_secret):
        parameters = {'AccessKeyId': access_key_id,
                      'Action': 'CreateToken',
                      'Format': 'JSON',
                      'RegionId': 'cn-shanghai',
                      'SignatureMethod': 'HMAC-SHA1',
                      'SignatureNonce': str(uuid.uuid1()),
                      'SignatureVersion': '1.0',
                      'Timestamp': time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                      'Version': '2019-02-28'}
        # 构造规范化的请求字符串
        query_string = AccessToken._encode_dict(parameters)
        # 构造待签名字符串
        string_to_sign = 'GET' + '&' + AccessToken._encode_text('/') + '&' + AccessToken._encode_text(query_string)
        # 计算签名
        secreted_string = hmac.new(bytes(access_key_secret + '&', encoding='utf-8'),
                                   bytes(string_to_sign, encoding='utf-8'),
                                   hashlib.sha1).digest()
        signature = base64.b64encode(secreted_string)
        # 进行URL编码
        signature = AccessToken._encode_text(signature)
        # 调用服务
        full_url = 'http://nls-meta.cn-shanghai.aliyuncs.com/?Signature=%s&%s' % (signature, query_string)
        # 提交HTTP GET请求
        response = requests.get(full_url)
        if response.ok:
            root_obj = response.json()
            key = 'Token'
            if key in root_obj:
                token = root_obj[key]['Id']
                expire_time = root_obj[key]['ExpireTime']
                return token, expire_time
        print(response.text)
        return None, None
    
token, expire_time = AccessToken.create_token(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)

def get_voice_token():
    token, expire_time = AccessToken.create_token(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
    return token


def generate_verification_code(length=4):
    characters = '0123456789'
    verification_code = ''.join(random.choices(characters, k=length))
    return verification_code


def create_client() -> Dysmsapi20170525Client:
    """
    使用AK&SK初始化账号Client
    @return: Client
    @throws Exception
    """
    # 工程代码泄露可能会导致 AccessKey 泄露，并威胁账号下所有资源的安全性。以下代码示例仅供参考。
    # 建议使用更安全的 STS 方式，更多鉴权访问方式请参见：https://help.aliyun.com/document_detail/378659.html。
    config = open_api_models.Config(
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_ID。,
        access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
        # 必填，请确保代码运行环境设置了环境变量 ALIBABA_CLOUD_ACCESS_KEY_SECRET。,
        access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET
    )
    # Endpoint 请参考 https://api.aliyun.com/product/Dysmsapi
    config.endpoint = f'dysmsapi.aliyuncs.com'
    return Dysmsapi20170525Client(config)

def send_sms(phone_number, code):
    client = create_client()
    code_str = '{"code":"%s"}' % code
    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        sign_name='北京图爱网络技术',
        phone_numbers=phone_number,
        template_code='SMS_302125817',
        template_param=code_str
    )
    try:
        res = client.send_sms_with_options(send_sms_request, util_models.RuntimeOptions())
    except Exception as error:
        # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
        # 错误 message
        print(error.message)
        # 诊断地址
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
