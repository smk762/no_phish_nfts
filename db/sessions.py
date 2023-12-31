import os
import sys
import time
from typing import List

import requests
import sqlalchemy
from sqlalchemy import delete, select, update, values
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from core.config import settings
from db.tables.contracts import Contract
from db.tables.domains import Domain
from enums import NetworkEnum
from logger import logger
from third_party.google import check_google_safebrowsing

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
        r = session.execute(
            (select(Contract.address)).where(Contract.network == network)
        )
        return [i.address for i in r]


def scan_contracts(network: str, addresses: str) -> dict:
    with Session(engine) as session:
        result = {}
        addresses = addresses.split(",")
        [result.update({i: False}) for i in addresses]
        sql = (
            select(Contract.address)
            .where(Contract.address.in_(addresses))
            .where(Contract.network == network)
        )
        matches = session.execute(sql)
        for i in matches:
            result.update({i.address: True})
        return result


def add_domain(url, source="", local=False, cache=200000000):
    domain = Domain(url=url, source=source, local=local, cache=cache)
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


def scan_domains(urls: str, local: bool = False) -> dict:
    result = {}
    urls = urls.split(",")
    urls = [url.replace("http://", "").replace("http://", "") for url in urls]
    [result.update({i: False}) for i in urls]

    eng = engine
    if local:
        eng = local_engine
    with Session(eng) as session:
        sql = select(Domain.url).where(Domain.url.in_(urls))
        matches = session.execute(sql)
        [result.update({i.url: True}) for i in matches]

    for url in [k for k, v in result.items() if not v]:
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
            result.update({url: True})
    return result


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
    else:
        q = input(
            "This will drop any existing tables and data, then create new, empty tables. Confirm [Y/y]? "
        )
        if not q.lower() == "y":
            return
    SQLModel.metadata.drop_all(eng)
    SQLModel.metadata.create_all(eng)
