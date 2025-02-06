import copy
from calendar import timegm
from datetime import datetime, timedelta
from typing import Optional

import bcrypt
from asyncpg import UniqueViolationError
from fastapi.responses import JSONResponse
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from src.core.config import app_settings
from src.dependencies import db_dependency
from src.exceptions import UserAlreadyExistsError
from src.models import Role, User
from src.schemas import CurrentUserSchema, UserLoginSchema, UserRegisterSchema

# Контекст для валидации и хеширования
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Генерация соли
def generate_salt() -> str:
    return bcrypt.gensalt().decode("utf-8")


# Хэширование пароля с использованием соли
def hash_password(password: str, salt: str) -> str:
    return bcrypt_context.hash(password + salt)


# Создание нового токена
def create_access_token(data: CurrentUserSchema, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    # копируем исходные данные, чтобы случайно их не испортить
    to_encode = copy.deepcopy(data)

    # устанавливаем временной промежуток жизни токена
    expire = timegm((datetime.utcnow() + expires_delta).utctimetuple())

    # добавляем время смерти токена
    to_encode.exp = expire

    # генерируем токен из данных, секрета и алгоритма
    return jwt.encode(to_encode.model_dump(), app_settings.jwt_secret, app_settings.algorithm)


# Регистрация пользователя
async def reg_user(user_data: UserRegisterSchema, db: db_dependency) -> JSONResponse:
    user_salt: str = generate_salt()
    try:
        user_role: Role = Role()
        db.add(user_role)
        await db.commit()
        create_user_statement: User = User(
            **user_data.model_dump(exclude={"password"}),  # распаковываем объект пользователя, исключая пароль
            salt=user_salt,
            role_id=user_role.id,
            hashed_password=hash_password(user_data.password, user_salt),
        )
        # создаём пользователя в базе данных
        db.add(create_user_statement)
        await db.commit()

        return JSONResponse(
            content={"message": "User created successfully"},
        )
    except UniqueViolationError:
        # если возникает ошибка UniqueViolationError, то считаем, что пользователь с такими данными уже есть
        raise UserAlreadyExistsError
    except Exception as ex:
        raise ex


# Аутентификация пользователя
async def authenticate_user(login_data: UserLoginSchema, db: db_dependency) -> Optional[User]:
    result = await db.execute(select(User).options(joinedload(User.role)).where(User.email == login_data.email))
    user: Optional[User] = result.scalars().first()
    # пользователь будет авторизован, если он зарегистрирован и ввёл корректный пароль
    if not user or not bcrypt_context.verify(login_data.password + user.salt, user.hashed_password):
        return None
    return user
