from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime

from database import Base, SessionLocal

import hashlib

DEVICE_TYPE_MOVING_SPEAKER = 1

class Device(Base):
    __tablename__ = "devices"
    
    id = Column(Integer, primary_key=True)
    type = Column(Integer, index=True)
    device_id = Column(String, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.now)

    @classmethod
    def get(cls, device_id):
        session = SessionLocal()
        user = session.query(cls).filter(cls.device_id == device_id).first()
        session.close()
        return user
# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True)
#     phone_number = Column(String, index=True)
#     nickname = Column(String, default='')
#     password_hash = Column(String, default='')
#     created_at = Column(DateTime, default=datetime.now)

#     @classmethod
#     def get(cls, phone_number):
#         session = SessionLocal()
#         user = session.query(cls).filter(cls.phone_number == phone_number).first()
#         session.close()
#         return user

#     @classmethod
#     def create(cls, phone_number, nickname='', password_hash=''):
#         user = cls(phone_number=phone_number, nickname=nickname, password_hash=password_hash)
#         with SessionLocal() as session:
#             session.add(user)
#             session.commit()
#         return user

