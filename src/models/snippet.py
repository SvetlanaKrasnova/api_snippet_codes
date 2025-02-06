import enum
import uuid

from sqlalchemy import Column, Enum, ForeignKey, Integer, String, UUID
from sqlalchemy.orm import relationship

from .base import Base


class LanguageEnum(enum.Enum):
    PYTHON = "python"
    JAVA = "java"
    C = "c"
    HTML = "html"
    CSS = "css"
    JS = "java_script"


class Snippet(Base):
    uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String)
    language = Column(Enum(LanguageEnum), nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    author = relationship("User", back_populates="snippets")
