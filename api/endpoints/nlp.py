
import os
import requests

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse

from pydantic import BaseModel, field_validator
from typing import Optional

from api import get_current_user, decode_token
from models import User

APPKEY = 'PQXXnL4bPDbRmARV'
TOKEN = '386e1d407b3b4ca08246b6a586d1aff8'

def send_voice_to_nlp(audio_file: UploadFile):
    url = 'nls-gateway-cn-shanghai.aliyuncs.com/stream/v1/asr'

import wave

import librosa
import soundfile as sf

def resample_audio(input_path, output_path, new_sample_rate=16000):
    # 加载音频文件，librosa会自动将音频转换为浮点数类型（-1.0到1.0之间）
    # 这里的sr=None保证以文件本身的采样率加载音频
    audio, original_sample_rate = librosa.load(input_path, sr=None)
    print('original_sample_rate = ', original_sample_rate)

    # 改变音频的采样率
    audio_resampled = librosa.resample(audio, orig_sr=original_sample_rate, target_sr=new_sample_rate)

    # 保存处理后的音频文件
    sf.write(output_path, audio_resampled, new_sample_rate)


router = APIRouter()

class ResTxt(BaseModel):
    text: str

@router.post('/voice-from-user')
async def voice_from_user(audio_file: UploadFile = File(...), token: str = Depends(get_current_user)) -> ResTxt:
    """
    获取用户语音输入并返回文本
    """
    phone_number = decode_token(token)
    user = User.get(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    # try:

    file_location = f"uploads/{audio_file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    with open(file_location, "wb+") as file_object:
        file_object.write(await audio_file.read())
        
    output_path = file_location.split('.')[0] + '_resampled.opus'
    use_path = file_location
    
    # with wave.open(file_location, mode='rb') as f:
    #     wav_params = f.getparams()
    #     print('wav_params = ', wav_params)
    #     if wav_params.framerate not in [16000, 8000]:
    # resample_audio(file_location, output_path)
    # use_path = output_path

    with open(use_path, mode = 'rb') as f:
        audioContent = f.read() # audio_file.read()
        host = 'http://nls-gateway-cn-beijing-internal.aliyuncs.com/stream/v1/asr?appkey=' + APPKEY + '&format=opus&sample_rate=16000'
        # 设置HTTPS请求头部
        httpHeaders = {
            'X-NLS-Token': TOKEN,
            'Content-type': 'application/octet-stream',
            'Content-Length': str(len(audioContent)),
            'Host': 'nls-gateway-cn-beijing-internal.aliyuncs.com'
            }
        res = requests.post(host, headers = httpHeaders, data = audioContent)
        res = res.json()
        text = res.get('result', '')
        print(text)
    # with wave.open(file_location, mode='rb') as f:
    #     print(f.getparams())
        # return JSONResponse(status_code=200, content={"message": "File uploaded successfully.", "file_path": file_location, "metadata": metadata.dict()})
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    res_txt = '123'
    return {
        'text': text
    }
