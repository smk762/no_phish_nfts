from typing import Optional, List
from uuid import UUID
import time

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.errors import EntityDoesNotExist
from db.tables.contracts import Contract
from db.schemas.contracts import ContractCreate, ContractPatch, ContractRead


class ContractRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_instance(self, address: str, network: str=None):
        statement = (
            select(Contract)
            .where(Contract.address == address)
        )
        if network:
            statement = (
                select(Contract)
                .where(Contract.address == address)
                .where(Contract.network == network)
            )
            
        results = await self.session.exec(statement)
        return results.first()

    async def create(self, contract_create: ContractCreate) -> ContractRead:
        db_contract = Contract.from_orm(contract_create)
        self.session.add(db_contract)
        await self.session.commit()
        await self.session.refresh(db_contract)
        return ContractRead(**db_contract.dict())

    async def list(self, network, limit: int = 10, offset: int = 0) -> List[ContractRead]:
        statement = (
            select(Contract)
            .where(Contract.network == network)
            .offset(offset)
            .limit(limit)
            .order_by(Contract.updated.desc())
        )
        results = await self.session.exec(statement)
        return [ContractRead(**contract.dict()) for contract in results]

    async def get(self, address: str, network: str=None) -> Optional[ContractRead]:
        db_contract = await self._get_instance(address, network)
        if db_contract is None:
            raise EntityDoesNotExist
        return ContractRead(**db_contract.dict())

    async def patch(
        self, contract_patch: ContractPatch
    ) -> Optional[ContractRead]:
        db_contract = await self._get_instance(contract_patch.address)
        if db_contract is None:
            raise EntityDoesNotExist
        contract_data = contract_patch.dict(exclude_unset=True, exclude={"id"})
        for key, value in contract_data.items():
            setattr(db_contract, key, value)

        self.session.add(db_contract)
        await self.session.commit()
        await self.session.refresh(db_contract)

        return ContractRead(**db_contract.dict())

    async def delete(self, address: str, network: str) -> None:
        db_contract = await self._get_instance(address, network)

        if db_contract is None:
            raise EntityDoesNotExist

        await self.session.delete(db_contract)

        await self.session.commit()
