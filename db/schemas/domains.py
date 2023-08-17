from uuid import UUID

from db.tables.domains import DomainBase


class DomainCreate(DomainBase):
    ...


class DomainRead(DomainBase):
    id: UUID


class DomainPatch(DomainBase):
    ...

class DomainAdd(DomainBase):
    ...
