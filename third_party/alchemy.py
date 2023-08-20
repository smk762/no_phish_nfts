#!/usr/bin/env python3
import requests
from core.config import settings
from logger import logger

def check_alchemy(network):
    api_key = settings.alchemy_api_key
    if network == "polygon":
        url = f"https://polygon-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
    elif network == "eth":
        url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
    else:
        return []
        # Other networks not yet supported
    return requests.get(url).json()