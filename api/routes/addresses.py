from fastapi import APIRouter, status
from third_party.mnemonichq import spam_scan
from enums import MnemonicHqNetworkEnum 

router = APIRouter()

@router.get(
    "/{network}/{address}",
    status_code=status.HTTP_200_OK,
    name="scan_for_spam",
    tags=["Addresses"],
    summary="Scans an address for spam on MnemonicHQ. Eth and Matic only.",
    description="If spam is detected, it will be added to the local DB.",
)
async def scan_for_spam(
    network: MnemonicHqNetworkEnum,
    address: str    
):
    return spam_scan(network, address)
