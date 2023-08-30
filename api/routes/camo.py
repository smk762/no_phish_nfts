from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse
from core.config import settings

import requests
import helper

router = APIRouter()

@router.get(
    "/{url_hex}",
    status_code=status.HTTP_200_OK,
    name="Hex Url Proxy",
    tags=["Decode URL"],
    summary="Takes URL in hex as input, and proxies to its json/image/audio/video content",
    description="For example, use '68747470733a2f2f73746174732e6b6d642e696f2f6170692f7461626c652f636f696e5f61637469766174696f6e2f' as an example to access the JSON data for coin activation available at https://stats.kmd.io/api/table/coin_activation/.",
)
async def decode_url(url_hex: str):
    hmac = helper.get_hmac(secret=settings.camo_key, url_hex=url_hex)
    url = f'/camo/{hmac}/{url_hex}'
    return RedirectResponse(url)
