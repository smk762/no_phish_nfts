from fastapi import FastAPI, status
from fastapi.openapi.utils import get_openapi
from fastapi.responses import RedirectResponse

from api.router import router
from core.config import settings
from middleware import LowerCaseMiddleware
from api.routes.camo import router as camo_router



app = FastAPI(
    title=settings.title,
    version=settings.version,
    description=settings.description,
    docs_url=settings.docs_url,
    openapi_url=settings.openapi_url,
    openapi_tags=settings.tags_metadata,
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
)

app.include_router(router, prefix=settings.api_prefix)
app.include_router(camo_router, prefix="/url", tags=["Encode / Decode Urls"])
app.middleware("http")(LowerCaseMiddleware())


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
        "altText": "Komodoplatform logo",
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
