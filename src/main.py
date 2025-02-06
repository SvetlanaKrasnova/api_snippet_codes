import atexit
import logging
import logging.config
import logging.handlers
import queue
from contextlib import asynccontextmanager
from logging.handlers import QueueListener
from typing import AsyncContextManager

import uvicorn
from fastapi import FastAPI, HTTPException, Request, status
from starlette.responses import JSONResponse

from src.api import api_router
from src.core.config import uvicorn_options
from src.core.logger import LOGGING_CONFIG

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("root")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncContextManager[None]:
    queue_listener = QueueListener(queue.Queue(), logging.FileHandler("snippet.log"))
    try:
        queue_listener.start()
        # регистрируем функцию, которая будет вызвана при завершении работы программы
        atexit.register(queue_listener.stop)
        yield
    finally:
        # в случае ошибки выключаем слушатель
        logger.info("ERROR - Application is shutting down.")
        queue_listener.stop()


app = FastAPI(lifespan=lifespan, docs_url="/api/openapi")

app.include_router(api_router)


@app.middleware("http")
async def error_middleware(request: Request, call_next):
    try:
        return await call_next(request)
    except HTTPException as exc:
        logger.exception(exc)
        return JSONResponse(
            status_code=exc.status_code,
            content={"message": exc.detail},
        )
    except Exception as e:
        logger.exception(f"{request.url} | Error in application: {e}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"message": str(e)},
        )


if __name__ == "__main__":
    logger.info(uvicorn_options)
    uvicorn.run(
        "main:app",
        **uvicorn_options,
    )
