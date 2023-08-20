from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from db.tables.base_class import NetworkEnum, TimestampModel, UUIDModel
from helper import now

class ContractBase(SQLModel):
    address: str = Field(nullable=False, default="")
    source: str = Field(nullable=False, default="")
    network: NetworkEnum = Field(default=NetworkEnum.eth)


class Contract(ContractBase, UUIDModel, TimestampModel, table=True):
    updated: int = Field(default_factory=lambda: now())
    __table_args__ = (UniqueConstraint("address", "network"),)
    __tablename__ = "contracts"
