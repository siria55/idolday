from datetime import datetime
import hashlib

from sqlalchemy import Column, Integer, String, DateTime

from database import Base

from .device import Device, DEVICE_TYPE_MOVING_SPEAKER



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
    email = Column(String, default='')
    username = Column(String, default='')
    password_hash = Column(String, default='')
    created_at = Column(DateTime, default=datetime.now)
    avatar_name = Column(String, default='persimmon')
    
    @classmethod
    def get(cls, db, id=None, phone_number=None, email=None, username=None):
        if id is not None:
            user = db.query(cls).filter(cls.id == id).first()
        elif phone_number is not None:
            print('111')
            user = db.query(cls).filter(cls.phone_number == phone_number).first()
            print('user22= ', user)
        elif email is not None:
            user = db.query(cls).filter(cls.email == email).first()
        elif username is not None:
            user = db.query(cls).filter(cls.username == username).first()
        else:
            return None
        return user
    
    @classmethod
    def get_all(cls, db):
        return db.query(cls).all()

    @classmethod
    def create(cls, db, phone_number='', email='', username='', password_hash=''):
        if phone_number == '' and email == '':
            raise ValueError('phone_number and email cannot be empty at the same time')
        user = cls(phone_number=phone_number, email=email, username=username, password_hash=password_hash)
        db.add(user)
        db.commit()
        return user

    @property
    def avatar_url(self):
        return '/static/avatar/' + self.avatar_name + '.png'

    def update(self, db, username=None, password=None, avatar_name=None, email=None, phone_number=None):
        self = db.merge(self)
        if username:
            self.username = username
        if password:
            self.password_hash = hash_password(password)
        if avatar_name:
            self.avatar_name = avatar_name
        if email:
            self.email = email
        if phone_number:
            self.phone_number = phone_number
        db.commit()
        db.refresh(self)

    def verify_password(self, password):
        return hash_password(password) == self.password_hash

    def bind_device(self, db, device_id):
        device = Device(type=DEVICE_TYPE_MOVING_SPEAKER, device_id=device_id, user_id=self.id)
        db.add(device)
        db.commit()
        return device

    def unbind_device(self, db, device_id):
        device = db.query(Device).filter(Device.device_id == device_id).first()
        if device:
            device.remove_tokens(db)
            db.delete(device)
            db.commit()
        return device

    def get_devices(self, db):
        return db.query(Device).filter(Device.user_id == self.id).all()
