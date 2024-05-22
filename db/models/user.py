from sqlalchemy import Column, Integer, String, DateTime, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base_class import Base

class User(Base):
    name = Column(String, nullable=False)
    nick_name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    status = Column(Enum('A', 'C', name='user_status'), default='A', nullable=False)
    registration_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    password = Column(String, nullable=False)

    tokens = relationship("AuthenticationToken", back_populates="user")
    account_recuperations = relationship("AccountRecuperation", back_populates="user")