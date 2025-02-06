from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing_extensions import Annotated

from src.db.db import get_async_session

db_dependency = Annotated[AsyncSession, Depends(get_async_session)]
