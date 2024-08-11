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


def send_action(client, device_id, topic):
    data = {
        "command": "action",
        "action": "move_forward",
        "value": {
            "duration": 10,
            "speed": 5,
        }
    }
    client.publish(f'{topic}/{device_id}/get', msgpack.packb(data))
