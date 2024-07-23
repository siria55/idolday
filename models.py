from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base, SessionLocal


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

    def update(self, nickname=None, password_hash=None):
        session = SessionLocal()
        if nickname:
            self.nickname = nickname
        if password_hash:
            self.password_hash = password_hash
        print(f'self.nickname = {self.nickname}')
        session.add(self)
        session.commit()
        session.close()
        print('after commit')
            
        return self