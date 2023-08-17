from uuid import UUID

from db.tables.contracts import ContractBase


class ContractCreate(ContractBase):
    ...


class ContractRead(ContractBase):
    id: UUID


class ContractPatch(ContractBase):
    ...
    
class ContractAdd(ContractBase):
    ...
