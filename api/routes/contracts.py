from typing import List, Optional, Set
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel

from api.dependencies.repositories import get_repository
from auth import edit_api_key_auth
from db.errors import EntityDoesNotExist
from db.repositories.contracts import ContractRepository
from db.schemas.contracts import ContractAdd, ContractPatch, ContractRead
from db.sessions import scan_contracts
from enums import NetworkEnum
from logger import logger

router = APIRouter()


class AddressList(BaseModel):
    network: str
    addresses: str


@router.get(
    "/{network}/list",
    response_model=List[Optional[ContractRead]],
    status_code=status.HTTP_200_OK,
    name="get_contract_list",
    summary="Returns a list of contract addresses tagged as spam.",
)
async def get_contract_list(
    network: NetworkEnum,
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> List[Optional[ContractRead]]:
    return await repository.list(limit=limit, offset=offset, network=network)


@router.post(
    "/scan",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    name="check_contracts",
    summary="Checks if a list of contract addresses are tagged as spam. Addresses should be separated by a comma. For example: `0x0ded8542fc8b2b4e781b96e99fee6406550c9b7c,0x8d1355b65da254f2cc4611453adfa8b7a13f60ee`",
)
async def check_contract(params: AddressList) -> dict:
    network = params.network.lower()
    networks = [i.value for i in NetworkEnum]
    if network in networks:
        addresses = params.addresses
        return {"result": scan_contracts(network, addresses)}
    else:
        logger.info(f"Network `{network}` is invalid. Use one of {networks}")


@router.post(
    "/create",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
    name="add_contract",
    summary="Adds a contract address to the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)],
)
async def add_contract(
    contract_create: ContractAdd = Body(...),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> ContractRead:
    return await repository.create(contract_create=contract_create)


@router.put(
    "/update",
    response_model=ContractRead,
    status_code=status.HTTP_200_OK,
    name="update_contract",
    summary="Updates a contract address in the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)],
)
async def update_contract(
    contract_patch: ContractPatch = Body(...),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> ContractRead:
    try:
        await repository.get(address=contract_patch.address)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{contract_patch.network} contract '{contract_patch.address}' not found!",
        )
    return await repository.patch(contract_patch=contract_patch)


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_contract",
    summary="Deletes a contract address from the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)],
)
async def delete_contract(
    network: NetworkEnum,
    contract_address: str,
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> None:
    try:
        await repository.get(network=network, address=contract_address)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"{network} contract '{contract_address}' not found!",
        )
    return await repository.delete(network=network, address=contract_address)
