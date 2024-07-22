from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    phone_number = Column(String, index=True)
    nickname = Column(String)
    hashed_password = Column(String)
    created_at = Column(DateTime, default=datetime.now)
