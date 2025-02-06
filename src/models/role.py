import enum

from sqlalchemy import Column, Enum, Integer
from sqlalchemy.orm import relationship

from .base import Base


class RoleEnum(enum.Enum):
    ADMIN = "admin"
    USER = "user"


class Role(Base):
    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    name = Column(Enum(RoleEnum), nullable=False, default=RoleEnum.USER)
    user = relationship("User", back_populates="role")
