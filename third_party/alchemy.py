#!/usr/bin/env python3
import requests
from core.config import settings
from logger import logger
from enums import AlchemyNetworkEnum
from logger import logger

def check_alchemy(network):
    api_key = settings.alchemy_api_key
    try:
        url = f"https://{network}-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
        return requests.get(url).json()
    except KeyError as e:
        logger.warning(f"{network} not supported by Alchemy")
        return {}
