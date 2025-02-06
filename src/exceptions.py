from starlette import status
from starlette.exceptions import HTTPException


class InternalError(Exception):
    pass


class SnippetNotFoundError(HTTPException):
    def __init__(self):
        super(SnippetNotFoundError, self).__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Snippet not found",
        )


class ValidateUserError(HTTPException):
    def __init__(self):
        super(ValidateUserError, self).__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate user",
        )


class LoginError(HTTPException):
    def __init__(self):
        super(LoginError, self).__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )


class BadRequestError(HTTPException):
    def __init__(self, ex):
        super(BadRequestError, self).__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Аn error has occurred: {ex}",
        )


class CredentialsError(HTTPException):
    def __init__(self):
        super(CredentialsError, self).__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserAlreadyExistsError(HTTPException):
    def __init__(self):
        super(UserAlreadyExistsError, self).__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with such credentials already exists",
        )


class RolePermissionsError(HTTPException):
    def __init__(self):
        super(RolePermissionsError, self).__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )
