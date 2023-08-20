from typing import Optional, List

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db.sessions import dump_domains

from db.errors import EntityDoesNotExist
from db.tables.domains import Domain
from db.schemas.domains import DomainCreate, DomainPatch, DomainRead
from logger import logger


class DomainRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_instance(self, url: str):
        statement = (
            select(Domain)
            .where(Domain.url == url)
        )
        results = await self.session.exec(statement)
        return results.first()

    async def create(self, domain_create: DomainCreate) -> DomainRead:
        logger.warning(domain_create)
        db_domain = Domain.from_orm(domain_create)
        self.session.add(db_domain)
        await self.session.commit()
        await self.session.refresh(db_domain)
        return DomainRead(**db_domain.dict())

    async def list(self, limit: int = 10, offset: int = 0) -> List[DomainRead]:
        statement = (
            (select(Domain))
            .offset(offset)
            .limit(limit)
            .order_by(Domain.updated.desc())
        )
        results = await self.session.exec(statement)
        return [DomainRead(**domain.dict()) for domain in results]

    async def get(self, url: str) -> Optional[DomainRead]:
        db_domain = await self._get_instance(url)
        if db_domain is None:
            raise EntityDoesNotExist
        return DomainRead(**db_domain.dict())

    async def patch(
        self, url: str, domain_patch: DomainPatch
    ) -> Optional[DomainRead]:
        db_domain = await self._get_instance(url)
        if db_domain is None:
            raise EntityDoesNotExist
        domain_data = domain_patch.dict(exclude_unset=True, exclude={"id"})
        for key, value in domain_data.items():
            setattr(db_domain, key, value)
        self.session.add(db_domain)
        await self.session.commit()
        await self.session.refresh(db_domain)
        return DomainRead(**db_domain.dict())

    async def delete(self, url: str) -> None:
        db_domain = await self._get_instance(url)
        if db_domain is None:
            raise EntityDoesNotExist
        await self.session.delete(db_domain)
        await self.session.commit()
