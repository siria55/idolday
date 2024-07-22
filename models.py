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
    def create(cls, phone_number, nickname='', password_hash=''):
        user = cls(phone_number=phone_number, nickname=nickname, password_hash=password_hash)
        session = SessionLocal()
        session.add(user)
        session.commit()
        session.close()
        return user
