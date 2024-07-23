from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base, SessionLocal

import hashlib


def hash_password(password):
    # 使用SHA-256算法进行加密
    sha256 = hashlib.sha256()
    sha256.update(password.encode('utf-8'))
    encrypted_password = sha256.hexdigest()
    return encrypted_password


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, index=True)
    nickname = Column(String, default='')
    password_hash = Column(String, default='')
    created_at = Column(DateTime, default=datetime.now)
    
    @classmethod
    def get(cls, phone_number):
        session = SessionLocal()
        user = session.query(cls).filter(cls.phone_number == phone_number).first()
        session.close()
        return user

    @classmethod
    def create(cls, phone_number, nickname='', password_hash=''):
        user = cls(phone_number=phone_number, nickname=nickname, password_hash=password_hash)
        with SessionLocal() as session:
            session.add(user)
            session.commit()
        return user

    def update(self, nickname=None, password=None):
        session = SessionLocal()
        self = session.merge(self)
        if nickname:
            self.nickname = nickname
        if password:
            self.password_hash = hash_password(password)
        session.commit()
        session.refresh(self)
        session.close()

    def verify_password(self, password):
        return hash_password(password) == self.password_hash
