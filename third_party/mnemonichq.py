#!/usr/bin/env python3
import requests

from core.config import settings
from db.sessions import add_contract, dump_contracts
from enums import MnemonicHqNetworkEnum
from logger import logger


# This API needs a wallet address as input, and only covers ETH/MATIC
# We can still use it to populate our database via user addresses though.
def spam_scan(network, address, local=False):
    contracts = dump_contracts(network)
    url = f"https://{network.name}-rest.api.mnemonichq.com/wallets/v1beta2/{address}/nfts?spam=SPAM_FILTER_ONLY"
    headers = {"X-API-Key": settings.mnemonichq_api_key, "accept": "application/json"}
    r = requests.get(url, headers=headers).json()
    spam_contracts = []
    if "nfts" in r:
        for nft in r["nfts"]:
            if nft["spam"]:
                contract = nft["nft"]["contractAddress"]
                spam_contracts.append(contract)
                logger.info(f"Mnemonichq detects {contract} on {network} is spam")
                if contract not in contracts:
                    add_contract("mnemonichq", network, contract, local)
    return {
        "network": network,
        "address": address,
        "result": f"{len(spam_contracts)} NFTs flagged as spam",
        "spam_contracts": spam_contracts,
    }
