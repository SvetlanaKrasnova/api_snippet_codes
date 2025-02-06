import json
from typing import Optional

import pytest
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import User
from src.schemas import UserLoginSchema, UserRegisterSchema
from src.services.auth import authenticate_user, reg_user

pytestmark = pytest.mark.asyncio


@pytest.mark.parametrize(
    argnames=("user_data", "is_delete", "user_in_db", "result"),
    argvalues=[
        (
            UserRegisterSchema(email="Test@yandex.ru", name="Test", password="test"),
            False,
            1,
            {"message": "User created successfully"},
        ),
        (
            UserRegisterSchema(email="Test1@yandex.ru", name="Test1", password="tes2232t"),
            True,
            2,
            {"message": "User created successfully"},
        ),
        (
            UserRegisterSchema(email="Test1@yandex.ru", name="Test1", password="tes2232t"),
            True,
            2,
            {"message": "User created successfully"},
        ),
    ],
    ids=("reg_user1", "reg_user2", "reg_user3"),
)
async def test_reg_user(dbsession: AsyncSession, user_data, is_delete, user_in_db, result):
    res = await reg_user(user_data=user_data, db=dbsession)
    assert json.loads(res.body.decode("utf8")) == result
    user = (await dbsession.execute(select(User))).scalars().all()
    assert len(user) == user_in_db
    if is_delete:
        await dbsession.execute(delete(User).where(User.email == user_data.email))
        await dbsession.commit()


@pytest.mark.parametrize(
    argnames=("login_data", "new_user", "result"),
    argvalues=[
        (
            UserLoginSchema(email="Test@yandex.ru", password="Test"),
            False,
            None,
        ),
        (
            UserLoginSchema(email="Test1@yandex.ru", password="tes2232t"),
            True,
            "Test1@yandex.ru",
        ),
    ],
    ids=("success_auth_user", "error_auth_user"),
)
async def test_authenticate_user(
    dbsession: AsyncSession,
    login_data: UserLoginSchema,
    new_user: bool,
    result: Optional[str],
):
    await dbsession.execute(delete(User).where(User.email == login_data.email))
    await dbsession.commit()
    if new_user:
        await reg_user(
            user_data=UserRegisterSchema(
                email=login_data.email,
                name="test_authenticate_user",
                password=login_data.password,
            ),
            db=dbsession,
        )
    auth_response = await authenticate_user(login_data=login_data, db=dbsession)
    if result:
        assert auth_response.email == result
    else:
        assert auth_response is result
