from typing import Union

from fastapi import FastAPI, Depends, HTTPException, Security, Header
from pydantic import BaseModel, field_validator

app = FastAPI()

from models import User
from sqlalchemy.orm import Session
from database import get_db

# def get_user(user_id: int, db: Session = Depends(get_db)):
#     return db.query(User).filter(User.id == user_id).first()


def get_current_user(token: str = Header(...)):  # 使用Header依赖提取token
    if not token.startswith("Bearer "):
        raise HTTPException(status_code=400, detail="Invalid token format")
    token = token.split(" ")[1]  # 获取token本身，去掉"Bearer "前缀
    if token != "expected_token":  # 假设expected_token是你期待的正确token
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return token  # 实际场景中这里可能返回解析token得到的用户信息


class RegisterSendCode(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v


class RegisterVerifyCode(BaseModel):
    phone_number: str
    code: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v
    

class UserInfo(BaseModel):
    phone_number: str
    password: str
    nickname: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:  # 假设我们需要6位数的密码
            raise ValueError('Password must be at least 6 digits')
        return v


class Login(BaseModel):
    phone_number: str
    password: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v

    @field_validator('password')
    def validate_password(cls, v):
        if len(v) < 6:  # 假设我们需要6位数的密码
            raise ValueError('Password must be at least 6 digits')
        return v

class LoginSendCode(BaseModel):
    phone_number: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v


class LoginVerifyCode(BaseModel):
    phone_number: str
    code: str

    @field_validator('phone_number')
    def validate_phone_number(cls, v):
        if len(v) != 11:  # 假设我们需要11位数的手机号码
            raise ValueError('Phone number must be 11 digits')
        return v

@app.post('/api/v1/register/send-code')
def register_send_code(register_send_code: RegisterSendCode):
    """
    注册，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = register_send_code.phone_number
    print('phone_number:', phone_number)
    # send code
    return {}

@app.post('/api/v1/register/verify-code')
def register_verify_code(register_verify_code: RegisterVerifyCode):
    """
    注册，验证验证码。验证成功返回 token
    """
    phone_number = register_verify_code.phone_number
    code = register_verify_code.code
    print('phone_number:', phone_number)
    print('code:', code)
    # verify code
    return {
        'token': '112312323231231232frfr'
    }

@app.post('/api/v1/user-info')
def user_info(user_info: UserInfo, token: str = Depends(get_current_user)):
    """
    修改用户信息
    """
    phone_number = user_info.phone_number
    password = user_info.password
    nickname = user_info.nickname
    print('phone_number:', phone_number)
    print('password:', password)
    print('nickname:', nickname)
    # complete register
    return {
        'token': '112312323231231232frfr'
    }

@app.post('/api/v1/login')
def login(login: Login):
    """
    手机号和密码登录，会返回 token
    """
    phone_number = login.phone_number
    password = login.password
    print('phone_number:', phone_number)
    print('password:', password)
    # login
    return {
        'token': '112312323231231232frfr'
    }

@app.post('/api/v1/login/send-code')
def login_send_code(login_send_code: LoginSendCode):
    """
    手机验证码登录，向这个手机号发送验证码。重发验证码也是这个 url，之前的验证码会失效
    """
    phone_number = login_send_code.phone_number
    print('phone_number:', phone_number)
    # send code
    return {}


@app.post('/api/v1/login/verify-code')
def login_verify_code(login_verify_code: LoginVerifyCode):
    """
    登录，验证验证码。验证成功返回 token
    """
    phone_number = login_verify_code.phone_number
    code = login_verify_code.code
    print('phone_number:', phone_number)
    print('code:', code)
    # verify code
    return {
        'token': '112312323231231232frfr'
    }



@app.get("/")
def read_root(db: Session = Depends(get_db)):
    # db = get_db()
    db_user = db.query(User).filter(User.id == 1).first()
    # res = get_user(user_id=1)
    print(db_user.email)
    return {"Hello": "World"}
