# -*- coding: utf-8 -*-
# This file is auto-generated, don't edit it. Thanks.
from datetime import datetime, timedelta
from alibabacloud_onsmqtt20200420.client import Client as OnsMqtt20200420Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_onsmqtt20200420 import models as ons_mqtt_20200420_models
from alibabacloud_tea_util import models as util_models
from alibabacloud_tea_util.client import Client as UtilClient

from .configs import ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET


def create_client() -> OnsMqtt20200420Client:
    """
    使用 AK&SK 初始化账号 Client
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
    # Endpoint 请参考 https://api.aliyun.com/product/OnsMqtt
    config.endpoint = f'onsmqtt.cn-beijing.aliyuncs.com'
    return OnsMqtt20200420Client(config)


def gen_mqtt_token(topic: str, device_id: str) -> str:
    client = create_client()
    future_time = datetime.now() + timedelta(days=10)
    future_timestamp = int(future_time.timestamp()) * 1000
    apply_token_request = ons_mqtt_20200420_models.ApplyTokenRequest(
        resources=f'{topic}/{device_id}/+',
        instance_id='post-cn-lsk3uo7yv02',
        expire_time= future_timestamp,#9007199254740990,
        actions='R,W'
    )
    runtime = util_models.RuntimeOptions()
    try:
        # 复制代码运行请自行打印 API 的返回值
        res = client.apply_token_with_options(apply_token_request, runtime)
        token = res.body.token
        return token
    except Exception as error:
        # 此处仅做打印展示，请谨慎对待异常处理，在工程项目中切勿直接忽略异常。
        # 错误 message
        print(error.message)
        # 诊断地址
        print(error.data.get("Recommend"))
        UtilClient.assert_as_string(error.message)
