import multiprocessing
from typing import Optional

from dotenv import load_dotenv
from pydantic import model_validator, PostgresDsn
from pydantic_core import MultiHostUrl
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing_extensions import Self

load_dotenv()


class AppSettings(BaseSettings):
    db_name: str
    db_user: str
    db_password: str
    db_host: str = "localhost"
    db_port: int = 5432
    app_port: int = 8000
    app_host: str = "localhost"
    reload: bool = True
    cpu_count: Optional[int] = None
    jwt_secret: str = "your_super_secret"
    algorithm: str = "HS256"
    postgres_dsn: PostgresDsn = None
    model_config = SettingsConfigDict()

    @model_validator(mode="before")
    @classmethod
    def set_postgres_dsn(cls, data: dict) -> Self:
        data["postgres_dsn"] = MultiHostUrl(
            f'postgresql+asyncpg://{data["db_user"]}:{data["db_password"]}@{data["db_host"]}:{data["db_port"]}/{data["db_name"]}',
        )
        return data


app_settings = AppSettings()

# набор опций для запуска сервера
uvicorn_options = {
    "host": app_settings.app_host,
    "port": app_settings.app_port,
    "workers": app_settings.cpu_count or multiprocessing.cpu_count(),
    "reload": app_settings.reload,
}
