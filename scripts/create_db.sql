from uuid import UUID

from db.tables.domains import ContractBase
from db.tables.domains import DomainBase


class ContractCreate(ContractBase):
    ...


class ContractRead(ContractBase):
    id: UUID


class ContractPatch(ContractBase):
    ...


class DomainCreate(DomainBase):
    ...


class DomainRead(DomainBase):
    id: UUID


class DomainPatch(DomainBase):
    ...
