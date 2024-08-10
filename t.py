import oss2
import requests
# 填写步骤1生成的签名URL。
# url = 'yourSignedUrl'
url = 'https://toai-voice.oss-cn-beijing.aliyuncs.com/voice_id.opus?x-oss-signature-version=OSS2&x-oss-expires=1723304157&x-oss-access-key-id=LTAI5tLQxLqhF7ywAw797nwj&x-oss-signature=5uzmd7D8O9pAOF8ANO9Xva0qJg8vDGqEZY2aey4Gv6s%3D'
# 指定Header。
headers = dict()
# 指定Content-Type。
headers['Content-Type'] = 'application/octet-stream'
# 指定存储类型。
headers["x-oss-storage-class"] = "Standard"

# 通过签名URL上传文件。
# 填写本地文件路径，例如D:\\examplefile.txt。
requests.put(url, data=open('./audio_res/1.opus', 'rb').read(), headers=headers)