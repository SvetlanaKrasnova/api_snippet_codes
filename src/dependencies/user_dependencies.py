import logging
from typing import List

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from typing_extensions import Annotated

from src.core.config import app_settings
from src.exceptions import CredentialsError, RolePermissionsError
from src.schemas import CurrentUserSchema

# специальный класс для настройки авторизации в Swagger
oauth2_bearer = OAuth2PasswordBearer(tokenUrl="/auth/token")
logger = logging.getLogger("root")


# Получение текущего пользователя
async def get_current_user(token: str = Depends(oauth2_bearer)):
    try:
        payload = jwt.decode(token, app_settings.jwt_secret, algorithms=[app_settings.algorithm])
        current_user = CurrentUserSchema(sub=payload.get("sub"), role=payload.get("role"))
        if not bool(current_user):
            raise CredentialsError
    except JWTError as e:
        logger.exception(e)
        raise CredentialsError
    return current_user


def has_role(required_role: List[CurrentUserSchema]):
    """
    1. получение текущего пользователя из токена доступа
    2. проверка роли полученного пользователя.
    :param required_role:
    :return:
    """

    def role_checker(current_user: user_dependency):
        if current_user.role not in required_role:
            raise RolePermissionsError
        return current_user

    return role_checker


user_dependency = Annotated[CurrentUserSchema, Depends(get_current_user)]
