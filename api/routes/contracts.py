from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from api.dependencies.repositories import get_repository
from db.errors import EntityDoesNotExist
from db.repositories.contracts import ContractRepository
from db.schemas.contracts import ContractAdd, ContractPatch, ContractRead
from db.sessions import is_contract_bad
from enums import NetworkEnum
from auth import edit_api_key_auth

router = APIRouter()


@router.get(
    "/{network}/list",
    response_model=List[Optional[ContractRead]],
    status_code=status.HTTP_200_OK,
    name="get_contract_list",
    summary="Returns a list of contract addresses tagged as spam."
)
async def get_contract_list(
    network: NetworkEnum,
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> List[Optional[ContractRead]]:
    return await repository.list(limit=limit, offset=offset, network=NetworkEnum[network])


@router.get(
    "/scan/{network}/{contract_address}",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    name="check_contract",
    summary="Checks if a contract address is tagged as spam."
)
async def check_contract(
    network: NetworkEnum,
    contract_address: str,
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> dict:
    return {
        "result": is_contract_bad(network, contract_address)
    }


@router.post(
    "/create",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
    name="add_contract",
    summary="Adds a contract address to the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)]
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
    dependencies=[Depends(edit_api_key_auth)]
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
            detail=f"{contract_patch.network} contract '{contract_patch.address}' not found!"
        )
    return await repository.patch(contract_patch=contract_patch)


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_contract",
    summary="Deletes a contract address from the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)]
)
async def delete_contract(
    network: NetworkEnum,
    contract_address: str,
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> None:
    try:
        await repository.get(network=NetworkEnum[network], address=contract_address)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{network} contract '{contract_address}' not found!"
        )
    return await repository.delete(network=NetworkEnum[network], address=contract_address)
