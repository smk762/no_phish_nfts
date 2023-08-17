from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from api.dependencies.repositories import get_repository
from db.errors import EntityDoesNotExist
from db.repositories.contracts import ContractRepository
from db.schemas.contracts import ContractAdd, ContractPatch, ContractRead

router = APIRouter()


@router.post(
    "/add_contract/{network}/{address}",
    response_model=ContractRead,
    status_code=status.HTTP_201_CREATED,
    name="add_contract",
)
async def add_contract(
    contract_create: ContractAdd = Body(...),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> ContractRead:
    # TODO: Add some simple auth in here to block spam
    return "not implemented yet"
    # return await repository.create(contract_create=contract_create)


@router.get(
    "/contract/{network}/contract_list",
    response_model=List[Optional[ContractRead]],
    status_code=status.HTTP_200_OK,
    name="get_contract_list",
)
async def get_contract_list(
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> List[Optional[ContractRead]]:
    return await repository.list(limit=limit, offset=offset)


@router.get(
    "/contract/{network}/{address}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    name="check_contract",
)
async def check_contract(
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> bool:
    # TODO: Is contract in blocklist?
    return await repository.list(limit=limit, offset=offset)


@router.delete(
    "/contract/{network}/{address}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_contract",
)
async def delete_contract(
    network: str,
    address: str,
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> None:
    # TODO: Add some simple auth in here to block spam
    return "not implemented yet"
    try:
        await repository.get(network=network, address=address)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{network} contract '{address}' not found!"
        )
    return await repository.delete(network=network, address=address)


@router.put(
    "/contract/{network}/{address}",
    response_model=ContractRead,
    status_code=status.HTTP_200_OK,
    name="update_contract",
)
async def update_contract(
    network: str,
    address: str,
    contract_patch: ContractPatch = Body(...),
    repository: ContractRepository = Depends(get_repository(ContractRepository)),
) -> ContractRead:
    try:
        await repository.get(network=network, address=address)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"{network} contract '{address}' not found!"
        )

    return await repository.patch(
        network=network, address=address, contract_patch=contract_patch
    )
