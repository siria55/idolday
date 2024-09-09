from time import time
from datetime import datetime, timedelta

from sqlalchemy import Column, Integer, String, DateTime

from database import Base

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
    def get(cls, db, device_id):
        device = db.query(cls).filter(cls.device_id == device_id).first()
        return device

    def get_last_valid_token(self, db):
        tokens = db.query(DeviceToken).filter(DeviceToken.device_id == self.device_id, DeviceToken.expired_at > datetime.now()).all()
        if not tokens:
            return ''
        tokens.sort(key=lambda x: x.expired_at, reverse=True)
        return tokens[0]


class DeviceToken(Base):
    __tablename__ = "device_tokens"
    
    id = Column(Integer, primary_key=True)
    device_id = Column(String, index=True)
    token = Column(String, index=True)
    expired_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

    @classmethod
    def get(cls, db, device_id, token=None):
        device_token = db.query(cls).filter(cls.device_id == device_id, cls.token==token).first()
        return device_token

    @classmethod
    def create(cls, db, device_id):
        token = hashlib.md5(device_id.encode() + str(int(time())).encode()).hexdigest()
        device_token = cls(device_id=device_id, token=token, expired_at=datetime.now() + timedelta(days=3000))
        db.add(device_token)
        db.commit()
        return device_token

    def revoke(self, db):
        self.expired_at = datetime.now()
        db.commit()
        db.refresh(self)

    @property
    def expired(self):
        return self.expired_at < datetime.now()
