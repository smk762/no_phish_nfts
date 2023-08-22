from fastapi import APIRouter, status

from enums import MnemonicHqNetworkEnum
from third_party.mnemonichq import spam_scan

router = APIRouter()


@router.get(
    "/{network}/{wallet_address}",
    status_code=status.HTTP_200_OK,
    name="scan_for_spam",
    tags=["Wallet Addresses"],
    summary="Scans an address for spam on MnemonicHQ. Eth / Polygon only.",
    description="If spam is detected, it will be added to the local DB. Use '0x3eb4b12127EdC81A4d2fD49658db07005bcAd065' as an example address to return a positive result (both ETH and POLYGON).",
)
async def scan_for_spam(network: MnemonicHqNetworkEnum, wallet_address: str):
    return spam_scan(network, wallet_address)
