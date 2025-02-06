import uuid
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from fastapi import status
from starlette.responses import JSONResponse

from src.schemas import SnippetPostSchema, SnippetSchema

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    argnames=("snippet_request", "snippet_response", "status_code"),
    argvalues=[
        (
            SnippetPostSchema(code='print("test")', language="python", author_id=1).model_dump(),
            SnippetSchema(
                uuid=uuid.UUID("161b356a-b0f6-4d34-908f-eb138285c9dd"),
                code='print("test")',
                language="python",
            ).model_dump(),
            status.HTTP_200_OK,
        ),
        (
            SnippetPostSchema(code="<u>TEST</u>", language="js", author_id=1).model_dump(),
            JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={"message": "mocked error created snippet"},
            ),
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ),
    ],
    ids=("success_create_snippet", "error_create_snippet"),
)
async def test_create_snippet(
    snippet_request,
    snippet_response,
    status_code,
):
    async def mock_post(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = snippet_response
        return mock_response

    with patch("httpx.AsyncClient.post", new=mock_post):
        async with httpx.AsyncClient() as client:
            response = await client.post("/snippets/", data=snippet_request)
        response_json = await response.json()
        assert response_json == snippet_response
        assert response.status_code == status_code


@pytest.mark.parametrize(
    argnames=("uuid", "result_get_snippet", "status_code"),
    argvalues=[
        (
            "161b356a-b0f6-4d34-908f-eb138285c9dd",
            SnippetSchema(
                uuid=uuid.UUID("161b356a-b0f6-4d34-908f-eb138285c9dd"),
                code='print("test")',
                language="python",
            ).model_dump(),
            status.HTTP_200_OK,
        ),
        (
            None,
            JSONResponse(
                status_code=status.HTTP_404_NOT_FOUND,
                content={"message": "Snippet not found"},
            ),
            status.HTTP_404_NOT_FOUND,
        ),
    ],
    ids=("success_get_snippet", "not_found_snippet"),
)
async def test_get_snippet(uuid, result_get_snippet, status_code):
    async def mock_get(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = result_get_snippet
        return mock_response

    with patch("httpx.AsyncClient.get", new=mock_get):
        async with httpx.AsyncClient() as client:
            response = await client.get(f"/snippets/{uuid}")
        response_json = await response.json()
        assert response_json == result_get_snippet
        assert response.status_code == status_code


@pytest.mark.parametrize(
    argnames=("uuid", "result_request", "status_code"),
    argvalues=[
        (
            "111b456a-mnf6-ld3x-9h7s-8b138l85c9rr",
            {"message": "Snippet deleted successfully"},
            status.HTTP_200_OK,
        ),
        (
            None,
            {"message": "mocked error deleted snippet'"},
            status.HTTP_500_INTERNAL_SERVER_ERROR,
        ),
        (
            "1234",
            {"message": "Snippet not found"},
            status.HTTP_404_NOT_FOUND,
        ),
    ],
    ids=("success_delete_snippet", "error_delete_snippet", "not_found_snippet"),
)
async def test_delete_snippet(uuid, result_request, status_code):
    async def mock_delete(*args, **kwargs):
        mock_response = AsyncMock()
        mock_response.status_code = status_code
        mock_response.json.return_value = result_request
        return mock_response

    with patch("httpx.AsyncClient.delete", new=mock_delete):
        async with httpx.AsyncClient() as client:
            response = await client.delete(f"/snippets/{uuid}")
        response_json = await response.json()
        assert response_json == result_request
        assert response.status_code == status_code
