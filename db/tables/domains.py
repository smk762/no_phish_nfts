from sqlmodel import Field, SQLModel
from db.tables.base_class import TimestampModel, UUIDModel


class DomainBase(SQLModel):
    url: str = Field(nullable=False)
    source: str = Field(nullable=False, default="")


class Domain(DomainBase, UUIDModel, TimestampModel, table=True):
    __tablename__ = "domains"
