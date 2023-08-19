from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, update, delete, values
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession
import requests
import time

from core.config import settings
from db.tables.domains import Domain
from db.tables.contracts import Contract

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
        session.add(contract)
        session.commit()


def dump_contracts(network):
    with Session(local_engine) as session:
        r = session.execute((select(Contract.address)).where(Contract.network == network))
        return [i.address for i in r]


def is_contract_bad(address: str) -> bool:
    with Session(engine) as session:
        sql = (
            select(Contract.address)
            .where(Contract.address == address)
            .limit(1)
        )
        return len([i.address for i in session.execute(sql)]) != 0


def add_domain(url, source="", local=False, cache=200000000):
    domain = Domain(
        url=url,
        source=source,
        updated=int(time.time()),
        local=local,
        cache=cache
    )
    eng = engine
    if local:
        eng = local_engine
        
    with Session(eng) as session:
        session.add(domain)
        session.commit()


def dump_domains():
    with Session(local_engine) as session:
        r = session.execute((select(Domain.url)))
        return [i.url for i in r]


def remove_stale_google_domains(local=False):
    eng = engine
    if local:
        eng = local_engine
        
    with Session(eng) as session:
        sql = delete(Domain).where(Domain.updated + Domain.cache < int(time.time()))
        session.execute(sql)
        session.commit()


# https://console.cloud.google.com/tos?id=safebrowsing
def check_google_safebrowsing(url: str, local=False) -> bool:
    baseurl = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
    params = f"key={settings.google_api_key}"
    headers = {"Content-Type": "application/json"}
    body = {
        "client": {
            "clientId": "no_phish_nft",
            "clientVersion": "0.0.1"
        },
        "threatInfo": {
            "threatTypes": [
                "MALWARE",
                "SOCIAL_ENGINEERING",
                "THREAT_TYPE_UNSPECIFIED",
                "UNWANTED_SOFTWARE",
                "POTENTIALLY_HARMFUL_APPLICATION"
            ],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [
                {"url": url}
            ]
        }
    }
    r = requests.post(f"{baseurl}?{params}", headers=headers, json=body).json()
    # 04323ss.com: {'matches': [{'threatType': 'SOCIAL_ENGINEERING', 'platformType': 'ANY_PLATFORM', 'threat': {'url': '04323ss.com'},
    # 'cacheDuration': '300s', 'threatEntryType': 'URL'}]}
    if "matches" in r:
        if "cacheDuration" in r["matches"][0]:
            cache = int(r["matches"][0]["cacheDuration"][:-1])
            add_domain(url, "google", local, cache)
        return True
    return False


def is_domain_bad(url: str) -> bool:
    url = url.replace("http://", "").replace("http://", "")
    with Session(engine) as session:
        sql = (select(Domain.url).where(Domain.url == url).limit(1))
        if len([i.url for i in session.execute(sql)]) == 0:
            return check_google_safebrowsing(url)
        return False


def create_tables():
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
