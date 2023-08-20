from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from api.dependencies.repositories import get_repository
from db.errors import EntityDoesNotExist
from db.repositories.contracts import ContractRepository
from db.schemas.contracts import ContractAdd, ContractPatch, ContractRead
from db.sessions import is_contract_bad
from db.tables.base_class import NetworkEnum
from third_party.mnemonichq import spam_scan

router = APIRouter()


@router.get(
    "/contract/scan_for_spam/{network}/{adddress}",
    status_code=status.HTTP_200_OK,
    name="scan_for_spam",
    tags=["Contracts"],
    summary="Scans an address for spam on MnemonicHQ",
    description="If spam is detected, it will be added to the local DB.",
)
async def scan_for_spam(
    network: NetworkEnum,
    address: str    
):
    return spam_scan(network, address)


@router.get(
    "/contract/{network}/contract_list",
    response_model=List[Optional[ContractRead]],
    status_code=status.HTTP_200_OK,
    name="get_contract_list",
    summary="Returns a list of contracts tagged as spam."
)
async def get_contract_list(
    network: NetworkEnum,
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> List[Optional[ContractRead]]:
    return await repository.list(limit=limit, offset=offset, network=network)


@router.get(
    "/contract/{network}/{address}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    name="check_contract",
    summary="Checks if a contract is tagged as spam."
)
async def check_contract(
    network: NetworkEnum,
    address: str,
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> dict:
    return {
        "result": is_contract_bad(network, address)
    }


@router.post(
    "/contract/{network}/{address}",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
    name="add_contract",
    summary="Adds a contract to the local DB. Requires auth."
)
async def add_contract(
    contract_create: ContractAdd = Body(...),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> ContractRead:
    # TODO: Add some simple auth in here to block spam
    return {"error": "not implemented yet"}
    # return await repository.create(contract_create=contract_create)


@router.put(
    "/contract/{network}/{address}",
    response_model=ContractRead,
    status_code=status.HTTP_200_OK,
    name="update_contract",
    summary="Updates a contract in the local DB. Requires auth."
)
async def update_contract(
    network: NetworkEnum,
    address: str,
    contract_patch: ContractPatch = Body(...),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> ContractRead:
    return {"error": "not implemented yet"}
    #try:
    #    await repository.get(network=network, address=address)
    #except EntityDoesNotExist:
    #    raise HTTPException(
    #        status_code=status.HTTP_404_NOT_FOUND, detail=f"{network} contract '{address}' not found!"
    #    )
    #return await repository.patch(
    #    network=network, address=address, contract_patch=contract_patch
    #)


@router.delete(
    "/contract/{network}/{address}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_contract",
    summary="Deletes a contract from the local DB. Requires auth."
)
async def delete_contract(
    network: NetworkEnum,
    address: str,
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> None:
    # TODO: Add some simple auth in here to block spam
    return {"error": "not implemented yet"}
    #try:
    #    await repository.get(network=network, address=address)
    #except EntityDoesNotExist:
    #    raise HTTPException(
    #        status_code=status.HTTP_404_NOT_FOUND, detail=f"{network} contract '{address}' not found!"
    #    )
    #return await repository.delete(network=network, address=address)

