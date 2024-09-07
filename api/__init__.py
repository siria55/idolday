import jwt

from fastapi import HTTPException, Header, Depends

from database import get_db

from models.user import User


def get_current_user(Authorization: str = Header(...), db = Depends(get_db)):  # 使用Header依赖提取token
    if not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid token format")
    token = Authorization.split(" ")[1]  # 获取token本身，去掉"Bearer "前缀
    # if token != "expected_token":  # 假设expected_token是你期待的正确token
    #     raise HTTPException(status_code=401, detail="Invalid or expired token")
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
    print('user 111 email = ', user.email)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    return user  # 实际场景中这里可能返回解析token得到的用户信息


def gen_token(phone_number_or_email):
    print(' gen token phone_number_or_email:', phone_number_or_email)
    encoded_jwt = jwt.encode({"phone_number_or_email": phone_number_or_email}, "secret", algorithm="HS256")
    return encoded_jwt


def decode_token(token):
    return jwt.decode(token, "secret", algorithms=["HS256"]).get('phone_number_or_email')
