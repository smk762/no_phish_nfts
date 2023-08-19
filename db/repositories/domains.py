from typing import Optional, List
from uuid import UUID

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from db.sessions import dump_domains

from db.errors import EntityDoesNotExist
from db.tables.base_class import StatusEnum
from db.tables.domains import Domain
from db.schemas.domains import DomainCreate, DomainPatch, DomainRead


class DomainRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_instance(self, domain_id: UUID):
        statement = (
            select(Domain)
            .where(Domain.id == domain_id)
            .where(Domain.status != StatusEnum.deleted)
        )
        results = await self.session.exec(statement)
        return results.first()

    async def create(self, domain_create: DomainCreate) -> DomainRead:
        db_domain = Domain.from_orm(domain_create)
        self.session.add(db_domain)
        await self.session.commit()
        await self.session.refresh(db_domain)
        return DomainRead(**db_domain.dict())

    async def list(self, limit: int = 10, offset: int = 0, all = 0) -> List[DomainRead]:
        statement = (
            (select(Domain).where(Transaction.status != StatusEnum.deleted))
            .offset(offset)
            .limit(limit)
        )
        results = await self.session.exec(statement)
        return [DomainRead(**domain.dict()) for domain in results]

    async def get(self, domain_id: UUID) -> Optional[DomainRead]:
        db_domain = await self._get_instance(domain_id)
        if db_domain is None:
            raise EntityDoesNotExist
        return DomainRead(**db_domain.dict())

    async def patch(
        self, domain_id: UUID, domain_patch: DomainPatch
    ) -> Optional[DomainRead]:
        db_domain = await self._get_instance(domain_id)
        if db_domain is None:
            raise EntityDoesNotExist
        domain_data = domain_patch.dict(exclude_unset=True, exclude={"id"})
        for key, value in domain_data.items():
            setattr(db_domain, key, value)
        self.session.add(db_domain)
        await self.session.commit()
        await self.session.refresh(db_domain)
        return DomainRead(**db_domain.dict())

    async def delete(self, domain_id: UUID) -> None:
        db_domain = await self._get_instance(domain_id)
        if db_domain is None:
            raise EntityDoesNotExist
        setattr(db_domain, "status", StatusEnum.deleted)
        self.session.add(db_domain)
        await self.session.commit()
