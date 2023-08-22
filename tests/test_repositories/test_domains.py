from uuid import UUID, uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from db.errors import EntityDoesNotExist
from db.repositories.domains import DomainRepository
from db.schemas.domains import DomainPatch


@pytest.mark.asyncio
async def test_create_domain(db_session: AsyncSession, create_domain):
    url = "example.com"
    source = "test"
    domain = create_domain(url, source)
    repository = DomainRepository(db_session)
    db_domain = await repository.create(domain)
    assert db_domain.url == domain.url
    assert isinstance(db_domain.id, UUID)


@pytest.mark.asyncio
async def test_get_domains(db_session: AsyncSession, create_domain):
    url = "example.com"
    source = "test"
    domain = create_domain(url, source)
    repository = DomainRepository(db_session)
    await repository.create(domain)
    db_domains = await repository.list()
    assert isinstance(db_domains, list)
    assert db_domains[0].url == domain.url


@pytest.mark.asyncio
async def test_get_domain(db_session: AsyncSession, create_domain):
    url = "example.com"
    source = "test"
    domain = create_domain(url, source)
    repository = DomainRepository(db_session)
    domain_created = await repository.create(domain)
    domain_db = await repository.get(url=domain_created.url)
    assert domain_created == domain_db


@pytest.mark.asyncio
async def test_get_domain_by_id_not_found(db_session: AsyncSession):
    repository = DomainRepository(db_session)
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(url="not existing url")


@pytest.mark.asyncio
async def test_update_domain(db_session: AsyncSession, create_domain):
    init_url = "www.example.com"
    init_source = "test"
    final_url = "www.example2.com"
    final_source = "test2"
    domain = create_domain(url=init_url, source=init_source)
    repository = DomainRepository(db_session)
    db_domain = await repository.create(domain)
    update_domain = await repository.patch(
        url=init_url,
        domain_patch=DomainPatch(url=final_url, source=final_source),
    )
    assert update_domain.url == final_url
    assert update_domain.source == final_source
