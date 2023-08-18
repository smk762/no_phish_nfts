from fastapi import FastAPI, status

from core.config import settings
from api.router import router
from db.sessions import create_tables

import logging

logger = logging.getLogger('fastapi')

app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url
)

app.include_router(router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    return {"result": "View documentation at /docs"}


@app.get(
    "/init_tables",
    status_code=status.HTTP_200_OK,
    name="init_tables"
)
async def init_tables():
    create_tables()

