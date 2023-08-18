from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status

from api.dependencies.repositories import get_repository
from db.errors import EntityDoesNotExist
from db.repositories.domains import DomainRepository
from db.schemas.domains import DomainAdd, DomainPatch, DomainRead
from db.sessions import is_domain_bad


router = APIRouter()


@router.post(
    "/add_domain/{source}/{domain}",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED,
    name="add_domain",
)
async def add_domain(
    
    domain_create: DomainAdd = Body(...),
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> DomainRead:
    # TODO: Add some simple auth in here to block spam
    
    return await repository.create(domain_create=domain_create)


@router.get(
    "/domain/domain_list",
    response_model=List[Optional[DomainRead]],
    status_code=status.HTTP_200_OK,
    name="get_domain_list",
)
async def get_domain_list(
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> List[Optional[DomainRead]]:
    return await repository.list(limit=limit, offset=offset)


@router.get(
    "/domain/{url}",
    response_model=bool,
    status_code=status.HTTP_200_OK,
    name="check_domain",
)
async def check_domain(
    url: str,
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> bool:
    return is_domain_bad(url)


@router.delete(
    "/domain/{domain}",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_domain",
)
async def delete_domain(
    domain: str,
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> None:
    # TODO: Add some simple auth in here to block spam
    return "not implemented yet"
    try:
        await repository.get(domain=domain)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Domain '{domain}' not found!"
        )
    return await repository.delete(domain=domain)


@router.put(
    "/domain/{domain}",
    response_model=DomainRead,
    status_code=status.HTTP_200_OK,
    name="update_domain",
)
async def update_domain(
    domain: str,
    domain_patch: DomainPatch = Body(...),
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> DomainRead:
    try:
        await repository.get(domain=domain)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Domain '{domain}' not found!"
        )

    return await repository.patch(
        domain=domain, domain_patch=domain_patch
    )
