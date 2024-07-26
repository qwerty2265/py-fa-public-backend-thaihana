from datetime import datetime

from sqlalchemy import Column, Integer, String, Boolean, TIMESTAMP

from models.base import Base


class User(Base):
    __tablename__ = "user"

    mobile_phone = Column(String, nullable=False, unique=True)

    first_name = Column(String(length=64), nullable=False)
    last_name = Column(String(length=64), nullable=False)

    bonus_points = Column(Integer, default=0)

    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    hashed_password = Column(String, nullable=False)
    otp = Column(Integer, nullable=True)
    otp_expires = Column(TIMESTAMP, default=datetime.utcnow())
