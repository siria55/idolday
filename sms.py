import os
import sys

from typing import List
import random


from alibabacloud_dysmsapi20170525.client import Client as Dysmsapi20170525Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dysmsapi20170525 import models as dysmsapi_20170525_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

ALIBABA_CLOUD_ACCESS_KEY_ID = 'LTAI5tDyTzsSSAoxFnJCYjT8'
ALIBABA_CLOUD_ACCESS_KEY_SECRET = '5apTh8RqiYHfaeywrsoPQatJttFk6A'


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
    send_sms_request = dysmsapi_20170525_models.SendSmsRequest(
        sign_name='北京图爱网络技术',
        phone_numbers=phone_number,
        template_code='SMS_302125817',
        template_param='{"code":"1234"}'
    )
    try:
        # 复制代码运行请自行打印 API 的返回值
        client.send_sms_with_options(send_sms_request, util_models.RuntimeOptions())
    except Exception as error:
        # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
        # 错误 message
        print(error.message)
        # 诊断地址
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
