from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import text
from sqlmodel import Field, SQLModel


class NetworkEnum(str, Enum):
    # If adding more, match to Moralis API chains
    avalanche = "avalanche"
    bsc = "bsc"
    eth = "ethereum"
    fantom = "fantom"
    polygon = "polygon"
    
    def __str__(self) -> str:
        return str.__str__(self)




class UUIDModel(SQLModel):
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class TimestampModel(SQLModel):
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False,
        sa_column_kwargs={"server_default": text("current_timestamp(0)")},
    )
