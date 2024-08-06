
# import os
# import requests
# import time

# from pydub import AudioSegment

# from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
# from fastapi.responses import JSONResponse

# from pydantic import BaseModel, field_validator
# from typing import Optional

# from api import get_current_user, decode_token
# from models.user import User
# from nlp import chat, get_face
# from memcached import mc

# APPKEY_STT = 'PQXXnL4bPDbRmARV'
# APPKEY_TTS = 'd3uUxszmFaXGRnzB'


# import librosa
# import soundfile as sf


# def resample_audio(input_path, output_path, new_sample_rate=16000):
#     # 加载音频文件，librosa会自动将音频转换为浮点数类型（-1.0到1.0之间）
#     # 这里的sr=None保证以文件本身的采样率加载音频
#     audio, original_sample_rate = librosa.load(input_path, sr=None)
#     print('original_sample_rate = ', original_sample_rate)

#     # 改变音频的采样率
#     audio_resampled = librosa.resample(audio, orig_sr=original_sample_rate, target_sr=new_sample_rate)

#     # 保存处理后的音频文件
#     sf.write(output_path, audio_resampled, new_sample_rate)


# router = APIRouter()

# class ResTalk(BaseModel):
#     origin_text: str
#     reply_text: str
#     reply_face_code_bit: str
#     reply_face_code_car: str
#     audio_path: str


# @router.post('/talk')
# async def voice_from_user(audio_file: UploadFile = File(...), token: str = Depends(get_current_user)) -> ResTalk:
#     """
#     获取用户语音输入并返回文本
#     """
#     phone_number = decode_token(token)
#     user = User.get(phone_number)
#     if not user:
#         raise HTTPException(status_code=404, detail="用户不存在")
#     # try:

#     file_location = f"uploads/{audio_file.filename}"
#     os.makedirs(os.path.dirname(file_location), exist_ok=True)
#     with open(file_location, "wb+") as file_object:
#         file_object.write(await audio_file.read())
        
#     output_path = file_location.split('.')[0] + '_resampled.opus'
#     use_path = file_location
    
#     # with wave.open(file_location, mode='rb') as f:
#     #     wav_params = f.getparams()
#     #     print('wav_params = ', wav_params)
#     #     if wav_params.framerate not in [16000, 8000]:
#     # resample_audio(file_location, output_path)
#     # use_path = output_path
#     token = mc.get('nls_token', '')
#     with open(use_path, mode = 'rb') as f:
#         audioContent = f.read() # audio_file.read()
#         host = 'http://nls-gateway-cn-beijing-internal.aliyuncs.com/stream/v1/asr?appkey=' + APPKEY_STT + '&format=opus&sample_rate=16000'
#         # 设置HTTPS请求头部
#         httpHeaders = {
#             'X-NLS-Token': token,
#             'Content-type': 'application/octet-stream',
#             'Content-Length': str(len(audioContent)),
#             'Host': 'nls-gateway-cn-beijing-internal.aliyuncs.com'
#             }
#         res = requests.post(host, headers = httpHeaders, data = audioContent)
#         res = res.json()
#         print('res = ', res)
#         origin_text = res.get('result', '')
#         print(origin_text)

#     if not origin_text:
#         raise HTTPException(status_code=400, detail="无法识别语音")

#     # NLP
#     reply_text = chat(origin_text, phone_number)
#     faces = get_face(phone_number)
#     print(faces)

#     # TTS
#     host = 'http://nls-gateway-cn-beijing-internal.aliyuncs.com/stream/v1/tts'
#     httpHeaders = {
#         'X-NLS-Token': token,
#         'Content-type': 'application/json',
#         'Content-Length': str(len(audioContent)),
#         'Host': 'nls-gateway-cn-beijing-internal.aliyuncs.com'
#         }
#     body = {
#         "appkey":APPKEY_TTS,
#         "text":reply_text,
#         "token":token,
#         "format":"wav"
#     }
#     res = requests.post(host, headers = httpHeaders, json = body)
#     print('Response status and response reason:')
#     contentType = res.headers['Content-Type']
#     audio_path = f"audio_res/{user.phone_number}_{int(time.time())}.wav"

#     body = res.content
#     if 'audio/mpeg' == contentType :
#         with open(audio_path, mode='wb') as f:
#             f.write(body)
#         print('The GET request succeed!')
#     else :
#         print('The GET request failed: ' + str(body))
        
#     wav_audio = AudioSegment.from_wav(audio_path)
#     opus_path = audio_path.split('.')[0] + '.opus'
#     wav_audio.export(opus_path, format="opus")

#     return {
#         'origin_text': origin_text,
#         'reply_text': reply_text,
#         'reply_face_code_bit': faces['face_code_bit'],
#         'reply_face_code_car': faces['face_code_car'],
#         'audio_path': '/download/' + opus_path,
#     }
