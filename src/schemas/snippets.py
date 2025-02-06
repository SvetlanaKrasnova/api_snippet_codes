import uuid
from typing import Optional

from pydantic import BaseModel


class _SnippetBaseSchema(BaseModel):
    uuid: uuid.UUID
    code: str
    language: str


class SnippetPostSchema(BaseModel):
    author_id: int
    code: str
    language: str


class SnippetPutSchema(_SnippetBaseSchema):
    language: Optional[str] = None
    code: Optional[str] = None


class SnippetPathSchema(_SnippetBaseSchema):
    pass


class SnippetSchema(_SnippetBaseSchema):
    pass
