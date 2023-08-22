from enum import Enum

from fastapi import Depends, HTTPException, Security, status
from fastapi.security.api_key import APIKeyHeader

from core.config import settings

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)


class ApiKeyEnum(str, Enum):
    edit = "edit"
    view = "view"

    def __str__(self) -> str:
        return str.__str__(self)


async def edit_api_key_auth(api_key: str = Security(api_key_header)):
    if api_key not in settings.valid_api_keys[ApiKeyEnum.edit]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your API key does not have access to this endpoint",
        )


# TODO: Not currently in use, but may be activated if required
async def view_api_key_auth(api_key: str = Security(api_key_header)):
    if api_key not in settings.valid_api_keys[ApiKeyEnum.view]:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Your API key does not have access to this endpoint",
        )
