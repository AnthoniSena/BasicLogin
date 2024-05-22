from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy import Column, Integer
from sqlalchemy.orm import as_declarative

@as_declarative()
class Base:
    id = Column(Integer, primary_key=True, nullable=False, unique=True)

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()