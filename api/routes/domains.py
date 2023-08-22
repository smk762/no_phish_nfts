from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from pydantic import BaseModel

from api.dependencies.repositories import get_repository
from auth import edit_api_key_auth
from db.errors import EntityDoesNotExist
from db.repositories.domains import DomainRepository
from db.schemas.domains import DomainAdd, DomainPatch, DomainRead
from db.sessions import scan_domains

router = APIRouter()


class UrlList(BaseModel):
    domains: str


@router.get(
    "/list",
    response_model=List[Optional[DomainRead]],
    status_code=status.HTTP_200_OK,
    name="get_domain_list",
    summary="Returns a list of domains tagged as spam.",
)
async def get_domain_list(
    limit: int = Query(default=10, lte=100),
    offset: int = Query(default=0),
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> List[Optional[DomainRead]]:
    return await repository.list(limit=limit, offset=offset)


@router.post(
    "/scan",
    response_model=dict,
    status_code=status.HTTP_200_OK,
    name="check_domains",
    summary="Checks if a domain is tagged as spam.",
)
async def check_domains(params: UrlList) -> dict:
    return scan_domains(params.domains)


@router.post(
    "/create",
    response_model=DomainRead,
    status_code=status.HTTP_201_CREATED,
    name="add_domain",
    summary="Adds a domain to the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)],
)
async def add_domain(
    domain_create: DomainAdd = Body(...),
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> DomainRead:
    return await repository.create(domain_create=domain_create)


@router.put(
    "/update",
    response_model=DomainRead,
    status_code=status.HTTP_200_OK,
    name="update_domain",
    summary="Updates a domain in the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)],
)
async def update_domain(
    domain_patch: DomainPatch = Body(...),
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> DomainRead:
    try:
        await repository.get(url=domain_patch.url)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Domain '{domain_patch.url}' not found!",
        )
    return await repository.patch(url=domain_patch.url, domain_patch=domain_patch)


@router.delete(
    "/delete",
    status_code=status.HTTP_204_NO_CONTENT,
    name="delete_domain",
    summary="Deletes a contract from the local DB. Requires auth.",
    dependencies=[Depends(edit_api_key_auth)],
)
async def delete_domain(
    url: str,
    repository: DomainRepository = Depends(get_repository(DomainRepository)),
) -> None:
    try:
        await repository.get(url=url)
    except EntityDoesNotExist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"Domain '{url}' not found!"
        )
    return await repository.delete(url=url)
