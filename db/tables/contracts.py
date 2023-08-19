from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from db.tables.base_class import NetworkEnum, TimestampModel, UUIDModel


class ContractBase(SQLModel):
    address: str = Field(nullable=False)
    source: str = Field(nullable=False, default="")


class Contract(ContractBase, UUIDModel, TimestampModel, table=True):
    network: NetworkEnum = Field(default=NetworkEnum.eth)
    __table_args__ = (UniqueConstraint("address", "network"),)
    __tablename__ = "contracts"
