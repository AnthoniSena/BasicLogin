from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
import os

ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES")

from .base_class import Base


class AuthenticationToken(Base):
    creation_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expiration_date = Column(DateTime, default=datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES)), nullable=False)
    status = Column(Enum('A', 'C', name='user_status'), default='A', nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    access_token = Column(String, index=True)
    refresh_toke = Column(String,nullable=False)

    user = relationship("User", back_populates="tokens")