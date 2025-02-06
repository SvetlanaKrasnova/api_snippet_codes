import logging

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse

from src.dependencies import db_dependency, has_role
from src.exceptions import SnippetNotFoundError
from src.models import RoleEnum
from src.schemas import SnippetPathSchema, SnippetPostSchema, SnippetPutSchema, SnippetSchema
from src.services.snippet import create_snippet_code, delete_snippet_by_uuid, get_snippet_by_uuid, update_snippet_code

snippets_router = APIRouter(prefix="/snippets", tags=["snippets"])
logger = logging.getLogger("root")


@snippets_router.get(
    "/{uuid}",
    responses={
        404: {"description": "Snippet not found"},
        400: {"description": "Invalid request"},
    },
)
async def get_snippet(uuid: str, db: db_dependency):
    if snippet := await get_snippet_by_uuid(db, uuid):
        return SnippetSchema(
            uuid=snippet.uuid,
            code=snippet.code,
            language=snippet.language.value,
        )
    raise SnippetNotFoundError


@snippets_router.post(
    "/",
    dependencies=[Depends(has_role([RoleEnum.USER.value, RoleEnum.ADMIN.value]))],
    responses={
        200: {"model": SnippetSchema},
        404: {"description": "Snippet not found"},
        400: {"description": "Invalid request"},
    },
)
async def create_snippet(snippet: SnippetPostSchema, db: db_dependency):
    snippet = await create_snippet_code(snippet=snippet, db=db)
    return SnippetSchema(
        uuid=snippet.uuid,
        code=snippet.code,
        language=snippet.language,
    )


@snippets_router.delete(
    "/{uuid}",
    dependencies=[Depends(has_role([RoleEnum.USER.value, RoleEnum.ADMIN.value]))],
    responses={
        404: {"description": "Snippet not found"},
        400: {"description": "Invalid request"},
    },
)
async def delete_snippet(uuid: str, db: db_dependency) -> JSONResponse:
    if await delete_snippet_by_uuid(db, uuid):
        return JSONResponse(
            content={"message": "Snippet deleted successfully"},
        )
    else:
        raise SnippetNotFoundError


@snippets_router.put(
    "/",
    dependencies=[Depends(has_role([RoleEnum.USER.value, RoleEnum.ADMIN.value]))],
    responses={
        200: {"model": SnippetSchema},
        404: {"description": "Snippet not found"},
        400: {"description": "Invalid request"},
    },
)
async def update_snippet(snippet_request: SnippetPutSchema, db: db_dependency) -> SnippetSchema:
    if snippet := await update_snippet_code(db, snippet_request):
        return SnippetSchema(
            uuid=snippet.uuid,
            code=snippet.code,
            language=snippet.language,
        )
    raise SnippetNotFoundError


@snippets_router.patch(
    "/",
    dependencies=[Depends(has_role([RoleEnum.USER.value, RoleEnum.ADMIN.value]))],
    responses={
        200: {"model": SnippetSchema},
        404: {"description": "Snippet not found"},
        400: {"description": "Invalid request"},
    },
)
async def update_snippet(snippet_request: SnippetPathSchema, db: db_dependency) -> SnippetSchema:
    if snippet := await update_snippet_code(db, snippet_request):
        return SnippetSchema(
            uuid=snippet.uuid,
            code=snippet.code,
            language=snippet.language,
        )
    raise SnippetNotFoundError
