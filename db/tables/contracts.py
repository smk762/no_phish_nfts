from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from enums import NetworkEnum
from db.tables.base_class import TimestampModel, UUIDModel
from helper import now

class ContractBase(SQLModel):
    address: str = Field(nullable=False, default="")
    source: str = Field(nullable=False, default="")
    network: NetworkEnum = Field(default=NetworkEnum.polygon)


class Contract(ContractBase, UUIDModel, TimestampModel, table=True):
    updated: int = Field(default_factory=lambda: now())
    __table_args__ = (UniqueConstraint("address", "network"),)
    __tablename__ = "contracts"
