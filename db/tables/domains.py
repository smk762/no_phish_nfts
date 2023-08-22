from sqlalchemy import UniqueConstraint
from sqlmodel import Field, SQLModel

from db.tables.base_class import TimestampModel, UUIDModel
from helper import now


class DomainBase(SQLModel):
    url: str = Field(nullable=False)
    source: str = Field(nullable=False)
    cache: int = Field(nullable=False, default=2000000000)


class Domain(DomainBase, UUIDModel, TimestampModel, table=True):
    updated: int = Field(default_factory=lambda: now())
    __table_args__ = (UniqueConstraint("url"),)
    __tablename__ = "domains"
