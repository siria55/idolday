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


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String, index=True)
    token = Column(String, index=True)
    expired_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

    @classmethod
    def get(cls, device_id):
        session = SessionLocal()
        user = session.query(cls).filter(cls.device_id == device_id).first()
        session.close()
        return user

    @classmethod
    def create(cls, device_id):
        session = SessionLocal()
        token = hashlib.md5(device_id.encode()).hexdigest()
        device_token = cls(device_id=device_id, token=token)
        session.add(device_token)
        session.commit()
        session.close()
        return device_token