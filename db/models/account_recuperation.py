from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from datetime import datetime, timezone
from .base_class import Base

class AccountRecuperation(Base):
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    creation_date = Column(DateTime, default=datetime.now(timezone.utc), nullable=False)
    expiration_date = Column(DateTime, nullable=False)
    validation_string = Column(String(8), unique=True, nullable=False)
    status = Column(Enum('A', 'C', name='user_status'), default='A', nullable=False)
    
    user = relationship("User", back_populates="account_recuperations")