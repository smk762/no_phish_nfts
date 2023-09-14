from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse, Response
from core.config import settings

import requests
import helper

router = APIRouter()

@router.get(
    "/decode/{url_hex}",
    status_code=status.HTTP_200_OK,
    name="Hex Url Proxy",
    tags=["Encode / Decode Urls"],
    summary="Takes URL in hex as input, and proxies to its json/image/audio/video content",
    description="For example, use '68747470733a2f2f73746174732e6b6d642e696f2f6170692f7461626c652f636f696e5f61637469766174696f6e2f' as an example to access the JSON data for coin activation available at https://stats.kmd.io/api/table/coin_activation/.",
)
async def decode_url(url_hex: str):
    hmac = helper.get_hmac(secret=settings.camo_key, url_hex=url_hex)
    url = f'{settings.domain}/camo/{hmac}/{url_hex}'
    print(url)
    r = requests.get(url)
    try:
        return r.json()
    except requests.exceptions.JSONDecodeError:
        pass
    try:
        print(f"Trying to send content as {r.headers['Content-Type']}")
        return Response(r.content, media_type=r.headers['Content-Type'])
    except Exception as e:
        print(f"Using redirect because {e}")
        return RedirectResponse(url)

@router.post(
    "/encode/{url_hex}",
    status_code=status.HTTP_200_OK,
    name="Convert Url to hex",
    tags=["Encode / Decode Urls"],
    summary="Takes URL string as input, and returns as a hex string",
    description="For example, the url https://stats.kmd.io/api/table/coin_activation/ will return '68747470733a2f2f73746174732e6b6d642e696f2f6170692f7461626c652f636f696e5f61637469766174696f6e2f' which can then be used as an input for the 'url/decode' endpoint.",
)
async def encode_url(url: str):
    print(f"URL pre-encode {url}")
    resp = url.encode('utf-8').hex()
    print(resp)
    print(bytes.fromhex(resp).decode('utf-8'))
    return resp

#https://file-examples.com/storage/fec36b918d65009119ed030/2017/04/file_example_mp4_480_1_5mg.mp4
# https://file-examples.com/storage/fec36b918d65009119ed030/2017/04/file_example_MP4_480_1_5MG.mp4