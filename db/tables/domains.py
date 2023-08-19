from sqlmodel import Field, SQLModel
from sqlalchemy import UniqueConstraint
from db.tables.base_class import TimestampModel, UUIDModel


class DomainBase(SQLModel):
    url: str = Field(nullable=False)
    source: str = Field(nullable=False, default="")
    cache: int = Field(nullable=False, default=2000000000)
    updated: int = Field(nullable=False, default=0)


class Domain(DomainBase, UUIDModel, TimestampModel, table=True):
    __table_args__ = (UniqueConstraint("url"),)
    __tablename__ = "domains"
