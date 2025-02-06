from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordRequestForm
from typing_extensions import Annotated

from src.dependencies import db_dependency, user_dependency
from src.exceptions import BadRequestError, LoginError, ValidateUserError
from src.schemas import CurrentUserSchema, UserLoginSchema, UserRegisterSchema
from src.services.auth import authenticate_user, create_access_token, reg_user

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.get("/current_user")
async def get_current_user(user: user_dependency) -> JSONResponse:
    return JSONResponse(content={"user": user.model_dump()})


@auth_router.post("/token")
async def token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency) -> JSONResponse:
    user = await authenticate_user(
        UserLoginSchema(
            email=form_data.username,
            password=form_data.password,
        ),
        db=db,
    )
    if not user:
        raise ValidateUserError
    access_token = create_access_token(
        data=CurrentUserSchema(
            sub=user.email,
            role=user.role.name.value,
        ),
    )
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})


@auth_router.post("/register")
async def register_user(user_data: UserRegisterSchema, db: db_dependency) -> JSONResponse:
    try:
        return await reg_user(user_data=user_data, db=db)
    except Exception as ex:
        raise BadRequestError(ex)


@auth_router.post("/login")
async def login_for_access_token(db: db_dependency, login_data: UserLoginSchema) -> JSONResponse:
    user = await authenticate_user(login_data, db)
    if not user:
        raise LoginError

    access_token = create_access_token(
        CurrentUserSchema(
            sub=user.email,
            role=user.role.name.value,
        ),
    )
    return JSONResponse(content={"access_token": access_token, "token_type": "bearer"})
