import jwt
import requests
from typing import Optional

from fastapi import HTTPException, Header, Depends, Form, Cookie

from database import get_db


from models.user import User


SECRET_KEY = 'ES_defd5fe453324be08becb845f6b5cf1f'

def verify_hcaptcha(hcaptcha_response: str = Form(...)):
    data = {
        'secret': SECRET_KEY,
        'response': hcaptcha_response
    }
    response = requests.post('https://hcaptcha.com/siteverify', data=data)
    result = response.json()
    
    if result['success']:
        return True
    else:
        print('captcha err = ', result)
        return False

def check_session(session: Optional[str] = Cookie(None), db = Depends(get_db)):
    if session is None:
        raise HTTPException(status_code=401, detail="session 错误，用户未登录")
    print('session = ', session)
    return session

def get_current_user(Authorization: str = Header(None), session: Optional[str] = Cookie(None), db = Depends(get_db)):  # 使用Header依赖提取token
    if Authorization and Authorization.startswith("Bearer "):
        token = Authorization.split(" ")[1]
    else:
        token = check_session(session, db)

    try:
        phone_number_or_email = decode_token(token)
        print('phone_number_or_email = decode_token(token):', phone_number_or_email)
    except Exception as e:
        raise HTTPException(status_code=401, detail="用户不存在")
    if not phone_number_or_email:
        raise HTTPException(status_code=401, detail="用户不存在")

    if '@' in phone_number_or_email:
        user = User.get(db, email=phone_number_or_email)
    else:
        user = User.get(db, phone_number=phone_number_or_email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    print('user 111 email = ', user.email)
    return user  # 实际场景中这里可能返回解析token得到的用户信息


def gen_token(phone_number_or_email):
    print(' gen token phone_number_or_email:', phone_number_or_email)
    encoded_jwt = jwt.encode({"phone_number_or_email": phone_number_or_email}, "secret", algorithm="HS256")
    return encoded_jwt


def decode_token(token):
    return jwt.decode(token, "secret", algorithms=["HS256"]).get('phone_number_or_email')
