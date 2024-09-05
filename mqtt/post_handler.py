import requests
import oss2
from datetime import datetime
import time
import msgpack

from aliyun_services.configs import (ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET,
    OSS_BUCKET_NAME, OSS_SERVICE_ENDPOINT)


def request_upload(client, device_id, topic):
    auth = oss2.AuthV2(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, OSS_SERVICE_ENDPOINT, OSS_BUCKET_NAME)
    filename = f'{int(time.time())}.opus'
    path = f'{device_id}/{datetime.now().strftime("%Y%m%d")}'
    voice_id = f'{path}/{filename}'
    headers = {
        'Content-Type': 'application/octet-stream',
        'x-oss-storage-class': 'Standard',
    }
    bucket.put_object('soundbox/' + path + '/', '')
    # 生成上传文件的签名URL，有效时间为60秒。
    # 生成签名URL时，OSS默认会对Object完整路径中的正斜线（/）进行转义，从而导致生成的签名URL无法直接使用。
    # 设置slash_safe为True，OSS不会对Object完整路径中的正斜线（/）进行转义，此时生成的签名URL可以直接使用。
    url = bucket.sign_url('PUT', 'soundbox/'+voice_id, 6000, slash_safe=True, headers=headers)
    print('uuuuulr = ', url)
    data = {
        "command": "request_upload",
        "upload_url": url,
        "voice_id": voice_id,
    }
    client.publish(f'{topic}/{device_id}/get', msgpack.packb(data))

def process_nlp(client, device_id, topic, user_id, voice_id):
    NLP_SERVER_URL = 'https://testing.toaitoys.com/api/SoundBoxPrototype/v1/process_audio'
    API_KEY = '2e5b3768d93c59a68553e2f70d2daa551231a451cbb64d8787a4139df9e8d62a'
    auth = oss2.AuthV2(ALIBABA_CLOUD_ACCESS_KEY_ID, ALIBABA_CLOUD_ACCESS_KEY_SECRET)
    bucket = oss2.Bucket(auth, OSS_SERVICE_ENDPOINT, OSS_BUCKET_NAME)
    oss_link = bucket.sign_url('GET', 'soundbox/'+voice_id, 3600 * 2, slash_safe=True)
    print('签名URL的地址为：', oss_link)
    post_data = {
        'device_id': device_id,
        'user_id': user_id,
        'product_sn': "00001234567",
        'oss_link': oss_link
    }
    headers = {
        'X-API-KEY': API_KEY,
    }
    res = requests.post(NLP_SERVER_URL, json=post_data, headers=headers)
    print('res.status_code = ', res.status_code)
    data = res.json()
    print('data = ', data)
    if 'action' not in data:
        print('nlp err = ', data)
        return
    action = data['action']
    client.publish(f'{topic}/{device_id}/get', msgpack.packb(action))


def send_msg(client, device_id, topic, msg):
    data = {
        "command": "test",
        "action": "send_msg",
        "value": {
            "msg": msg,
        }
    }
    client.publish(f'{topic}/{device_id}/get', msgpack.packb(data))
