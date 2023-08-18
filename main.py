from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi

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


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.title,
        version=settings.version,
        description=settings.description,
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://komodoplatform.com/assets/img/logo-dark.webp",
        "backgroundColor": "#CCCCCC",
        "altText": "Komodoplatform logo"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


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

