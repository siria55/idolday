
from queue import Queue
import requests

data_queue = Queue()

data_queue.put(b'chunk1')

# 发送流式数据到远程服务器的生成器
def stream_data(data_queue):
    while True:
        chunk = data_queue.get()
        if chunk is None:  # 收集结束标志
            break
        yield chunk
response = requests.post(
    'http://127.0.0.1:8001/api/v1/firmware/audio_upload', 
    data=stream_data(data_queue),  # 使用生成器作为data参数
    headers={'Content-Type': 'application/octet-stream'},  # 根据需要调整
    stream=True  # 表明是流式请求
)