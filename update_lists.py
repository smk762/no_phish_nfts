#!/usr/bin/env python3
import os
import json
import time
from pathlib import Path
import requests 
import tarfile
import asyncio
from os import listdir
from os.path import isfile, join, basename, exists, realpath, dirname
from db.sessions import add_domain, dump_domains, add_contract, \
    dump_contracts, check_google_safebrowsing, remove_stale_google_domains
from typing import Optional, List
from fastapi import Depends
from api.dependencies.repositories import get_repository
from db.repositories.domains import DomainRepository
from db.schemas.domains import DomainAdd, DomainRead
from core.config import settings
from logger import logger


script_path = realpath(dirname(__file__))

def create_list_folder(list_type):    
    Path(f"{script_path}/lists/{list_type}").mkdir(parents=True, exist_ok=True)


def files_in_folder(folder):
    return [f for f in listdir(folder) if isfile(join(folder, f))]


def get_text_file(link):
    data = requests.get(link)
    return data.text


def get_json_file(link):
    data = requests.get(link)
    return data.json()


def extract_tar_url(url, extract_path, fn):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(f"{extract_path}/{fn}", 'wb') as f:
            f.write(response.raw.read())
        with tarfile.open(f"{extract_path}/{fn}", mode="r:gz") as tf:
            tf.extractall(extract_path)


def update_source_data():
    with open(f"{script_path}/sources.json") as f:
        sources = json.load(f)
    for list_type in ["domains", "contracts"]:
        create_list_folder(list_type)
        for list_category in ["init", "cron"]:
            urls = sources[list_type][list_category]
            update_source_files(list_type, urls, list_category == "cron")


def update_source_files(list_type, urls, cron=True):
    for url in urls:
        fn = basename(url)
        list_path = f"{script_path}/lists/{list_type}"
        if exists(f"{list_path}/{fn}") and not cron:
            continue
        if fn.endswith(".tar.gz"):
            extract_tar_url(url, list_path, fn)
        elif fn.endswith(".txt"):
            with open(f"{list_path}/{fn}", 'w') as f:
                f.write(get_text_file(url))
        elif fn.endswith(".json"):
            with open(f"{list_path}/{fn}", 'w') as f:
                json.dump(get_json_file(url), f)
        logger.info(f"Updated {url}")


def update_db():
    known_domains = dump_domains()
    known_contracts = {}
    for network in ["Polygon", "Eth", "Bsc", "Avalanche", "Fantom"]:
        known_contracts[network] = dump_contracts(network)
        migrate_alchemy_spam_contracts(network, known_contracts[network])
        # Doing again to include the contracs added from alchemy
        known_contracts[network] = dump_contracts(network)
        
        
    for list_type in ["contracts", "domains"]:
        folder = f"{script_path}/lists/{list_type}"
        files = files_in_folder(folder)
        for file in files:
            if file.endswith(".txt"):
                with open(f"{folder}/{file}") as f:
                    data = set([i.strip() for i in f.readlines()])
                    if list_type == "contracts":
                        # TODO: Currently there is no txt file source for contracts
                        # When there is, we'll need to define network here
                        add_contracts(file, "unknown", data, known_contracts[network])
                    elif list_type == "domains":
                        add_domains(data, file, known_domains)
            elif file.endswith(".json"):
                with open(f"{folder}/{file}") as f:
                    data = json.load(f)
                    if list_type == "contracts":
                        if network in data:
                            add_contracts(file, network, data, known_contracts[network])
                    elif list_type == "domains":                        
                        if "blacklist" in data:
                            data = data["blacklist"]
                        add_domains(data, file, known_domains)
            else:
                logger.warning(f"Skipping {file}, it is not a text file...")


def migrate_alchemy_spam_contracts(network, known_contracts):
    source = "alchemy"
    api_key = settings.alchemy_api_key
    if network == "Polygon":
        url = f"https://polygon-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
    elif network == "Eth":
        url = f"https://eth-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
    else:
        return
        # Other networks not yet supported
        '''
        elif network == "Arb":
            url = f"https://arb-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
        elif network == "Opt":
            url = f"https://opt-mainnet.g.alchemy.com/nft/v2/{api_key}/getSpamContracts"
        '''
    data = requests.get(url).json()
    addresses = list(set(data) - set(known_contracts))
    logger.info(f"{len(addresses)} contract addresses to process for {network} from {source}...")
    logger.info(f"{len(known_contracts)} known_contracts for {network} from {source}...")
    for address in addresses:
        try:
            add_contract(source, network, address, True)
            logger.info(f"[{source}] Added {address} for {network}")
        except Exception as e:
            logger.error(e)


def add_contracts(source, network, contracts, known_contracts):
    contracts = list(set(contracts) - set(known_contracts))
    for address in contracts:
        add_contract(source, network, address, True)
        logger.info(f"[{source}] Added {address} for {network}")


def add_domains(domains, source, known_domains):
    if known_domains:
        logger.info(f"{len(known_domains)} domains in the blocklist")
    # Remove protocol prefix
    domains = [i.replace("http://", "").replace("https://", "") for i in domains]
    # Remove path suffix
    domains = [i.split("/")[0] for i in domains]
    domains = list(set(domains) - set(known_domains))
    for domain in domains:
        logger.info(f"Adding {domain} from {source}...")
        add_domain(domain, source, True)



if __name__ == '__main__':
    # TODO: Move to tests
    logger.info(f'Is ethercb.com google safe?: {check_google_safebrowsing("04323ss.com", True, False)}')
    logger.info(f'Is twitter.com google safe?: {check_google_safebrowsing("twitter.com", True, False)}')
    # Process domains.
    remove_stale_google_domains(True)
    update_source_data()
    update_db()

