from typing import Optional, Tuple

from sqlalchemy.future import select

from src.dependencies import db_dependency
from src.models import Snippet
from src.schemas import SnippetPathSchema, SnippetPostSchema, SnippetPutSchema


async def get_snippet_by_uuid(db: db_dependency, uuid: str) -> Optional[Snippet]:
    if snippet := await db.execute(select(Snippet).filter(Snippet.uuid == uuid)):
        return snippet.scalars().first()
    return None


async def delete_snippet_by_uuid(db: db_dependency, uuid: str) -> bool:
    if db_snippet := await get_snippet_by_uuid(db, uuid):
        await db.delete(db_snippet)
        await db.commit()
        return True
    return False


async def create_snippet_code(db: db_dependency, snippet: SnippetPostSchema) -> Snippet:
    db_snippet = Snippet(
        code=snippet.code,
        language=snippet.language,
        author_id=snippet.author_id,
    )
    db.add(db_snippet)
    await db.commit()
    return db_snippet


async def update_snippet_code(
    db: db_dependency,
    update_snippet: Tuple[SnippetPutSchema, SnippetPathSchema],
) -> Optional[Snippet]:
    if snippet := await get_snippet_by_uuid(db, update_snippet.uuid):
        if snippet.code:
            snippet.code = update_snippet.code
        if update_snippet.language:
            snippet.language = update_snippet.language
        await db.commit()
        return snippet
    return None
