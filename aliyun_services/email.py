# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
import os
import sys

from typing import List

from alibabacloud_dm20151123.client import Client as Dm20151123Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_dm20151123 import models as dm_20151123_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient


from .configs import ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET

def create_client() -> Dm20151123Client:
    config = open_api_models.Config(
        access_key_id=ALIBABA_CLOUD_ACCESS_KEY_ID,
        access_key_secret=ALIBABA_CLOUD_ACCESS_KEY_SECRET
    )
    # Endpoint 请参考 https://api.aliyun.com/product/Dm
    config.endpoint = f'dm.aliyuncs.com'
    return Dm20151123Client(config)

def send_email(to_email, subject, html_body):
    client = create_client()
    single_send_mail_request = dm_20151123_models.SingleSendMailRequest(
        account_name='notify@notify.toaitoys.com',
        address_type=1,
        reply_to_address=False,
        to_address=to_email,
        subject=subject,
        html_body=html_body,
    )
    runtime = util_models.RuntimeOptions()
    try:
        # 复制代码运行请自行打印 API 的返回值
        client.single_send_mail_with_options(single_send_mail_request, runtime)
    except Exception as error:
        # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
        # 错误 message
        print(error.message)
        # 诊断地址
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
