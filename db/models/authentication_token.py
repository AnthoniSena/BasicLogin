from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone, timedelta
from config.config import settings
from .base_class import Base

class AuthenticationToken(Base):
    creation_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expiration_date = Column(DateTime, default=datetime.now(timezone.utc) + timedelta(minutes=int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)), nullable=False)
    status = Column(Enum('A', 'C', name='token_status'), default='A', nullable=False)
    user_id = Column(Integer, ForeignKey("user.id"))
    access_token = Column(String, index=True)

    user = relationship("User", back_populates="tokens")