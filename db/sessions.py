from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
import sqlalchemy
from sqlalchemy import select, update, delete, values
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
import requests
import time
import sys
import os

from core.config import settings
from db.tables.domains import Domain
from db.tables.contracts import Contract
from third_party.google import check_google_safebrowsing
from logger import logger

engine = create_engine(
    url=settings.sync_database_url,
    echo=settings.db_echo_log,
)

local_engine = create_engine(
    url=settings.sync_database_url_local,
    echo=settings.db_echo_log,
)

async_engine = create_async_engine(
    url=settings.async_database_url,
    echo=settings.db_echo_log,
    future=True,
)

async_session = sessionmaker(
    bind=async_engine, class_=AsyncSession, expire_on_commit=False
)


def add_contract(source, network, address, local=False):
    contract = Contract(source=source, network=network, address=address)
    eng = engine
    if local:
        eng = local_engine
    with Session(eng) as session:
        try:
            session.add(contract)
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            logger.warning(e)
        except Exception as e:
            logger.warning(e)


def dump_contracts(network, local=False):
    eng = engine
    if local:
        eng = local_engine
    with Session(eng) as session:
        r = session.execute((select(Contract.address)).where(Contract.network == network))
        return [i.address for i in r]


def is_contract_bad(network: str, address: str) -> bool:
    with Session(engine) as session:
        sql = (
            select(Contract.address)
            .where(Contract.address == address)
            .where(Contract.network == network)
            .limit(1)
        )
        return len([i.address for i in session.execute(sql)]) != 0


def add_domain(url, source="", local=False, cache=200000000):
    domain = Domain(
        url=url,
        source=source,
        local=local,
        cache=cache
    )
    eng = engine
    if local:
        eng = local_engine

    with Session(eng) as session:
        try:
            session.add(domain)
            session.commit()
        except sqlalchemy.exc.IntegrityError as e:
            logger.warning(e)
        except Exception as e:
            logger.warning(e)


def dump_domains(local=False):
    eng = engine
    if local:
        eng = local_engine
    with Session(eng) as session:
        r = session.execute((select(Domain.url)))
        return [i.url for i in r]



def is_domain_bad(url: str, local: bool = False) -> bool:
    url = url.replace("http://", "").replace("http://", "")
    with Session(engine) as session:
        sql = (
            select(Domain)
            .where(Domain.url == url)
            .limit(1)
        )
        r = session.execute(sql)
        data = [i for i in r]
        if len(data) == 0:
            logger.warning(f"No entries for {url} in DB")
            r = check_google_safebrowsing(url)
            logger.debug(f"{url}: {r}")
            if "matches" in r:
                if "cacheDuration" in r["matches"][0]:
                    cache = int(r["matches"][0]["cacheDuration"][:-1])
                    remove_stale_google_domains(local)
                    try:
                        add_domain(url, "google", local, cache)
                    except Exception as e:
                        logger.error(e)
                return True
            return False
        return True


def remove_stale_google_domains(local=False):
    eng = engine
    if local:
        eng = local_engine
    with Session(eng) as session:
        sql = delete(Domain).where(Domain.updated + Domain.cache < int(time.time()))
        session.execute(sql)
        session.commit()
        logger.info("Stale google domains cache cleared")


def create_tables(local=False):
    eng = engine
    if local:
        eng = local_engine
    SQLModel.metadata.drop_all(eng)
    SQLModel.metadata.create_all(eng)
