from fastapi import HTTPException, Header
import jwt

def get_current_user(token: str = Header(...)):  # 使用Header依赖提取token
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid token format")
    token = token.split(" ")[1]  # 获取token本身，去掉"Bearer "前缀
    if token != "expected_token":  # 假设expected_token是你期待的正确token
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token  # 实际场景中这里可能返回解析token得到的用户信息

def gen_token(phone_number):
    encoded_jwt = jwt.encode({"phone_number": phone_number}, "secret", algorithm="HS256")
    return encoded_jwt
