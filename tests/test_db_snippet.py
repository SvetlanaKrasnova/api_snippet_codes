import uuid
from typing import Tuple

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Snippet
from src.schemas import SnippetPathSchema, SnippetPostSchema, SnippetPutSchema
from src.services.snippet import create_snippet_code, delete_snippet_by_uuid, get_snippet_by_uuid, update_snippet_code

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    argnames=("snippet_request",),
    argvalues=[
        (
            SnippetPostSchema(
                code="Test",
                language="JS",
                author_id=2,
            ),
        ),
        (
            SnippetPostSchema(
                code="Test",
                language="PYTHON",
                author_id=1,
            ),
        ),
    ],
    ids=("success_create_snippet", "error_create_snippet"),
)
async def test_create_snippet_code(dbsession: AsyncSession, snippet_request: SnippetPostSchema):
    await create_snippet_code(dbsession, snippet_request)
    result = (
        (await dbsession.execute(select(Snippet).where(Snippet.author_id == snippet_request.author_id))).scalars().all()
    )
    assert len(result) == 1
    await delete_snippet_by_uuid(db=dbsession, uuid=result[0].uuid)


@pytest.mark.parametrize(
    argnames=("before_snippet", "update_data", "is_exists_snippet"),
    argvalues=[
        (
            SnippetPostSchema(
                author_id=1,
                code="function() { return false; }",
                language="JS",
            ),
            SnippetPathSchema(
                uuid=uuid.uuid4(),
                language="PYTHON",
                code="def func: return True",
            ),
            True,
        ),
        (
            SnippetPostSchema(
                author_id=1,
                code="function() { return false; }",
                language="JS",
            ),
            SnippetPutSchema(
                uuid=uuid.uuid4(),
                code="class Test: TEST=True",
            ),
            False,
        ),
        (
            SnippetPostSchema(
                author_id=1,
                code=".container { text-align: center;}",
                language="CSS",
            ),
            SnippetPutSchema(
                uuid=uuid.uuid4(),
                code=".block { width: 50%; margin: 0 auto; }",
            ),
            True,
        ),
        (
            SnippetPostSchema(
                author_id=1,
                code=".container { text-align: center;}",
                language="CSS",
            ),
            SnippetPutSchema(
                uuid=uuid.uuid4(),
                language="HTML",
            ),
            True,
        ),
    ],
    ids=(
        "success_update_path_snippet",
        "error_not_found_snippet",
        "success_update_put_code_snippet",
        "success_update_put_language_snippet",
    ),
)
async def test_update_snippet_code(
    dbsession: AsyncSession,
    update_data: Tuple[SnippetPutSchema, SnippetPathSchema],
    before_snippet,
    is_exists_snippet,
):
    if is_exists_snippet:
        before_snippet = await create_snippet_code(db=dbsession, snippet=before_snippet)
        update_data.uuid = before_snippet.uuid
    res_update = await update_snippet_code(db=dbsession, update_snippet=update_data)
    if is_exists_snippet:
        after_snippet = await get_snippet_by_uuid(db=dbsession, uuid=before_snippet.uuid)
        assert before_snippet.code == after_snippet.code
        assert before_snippet.language == after_snippet.language
        await delete_snippet_by_uuid(db=dbsession, uuid=after_snippet.uuid)
    else:
        assert res_update is None
