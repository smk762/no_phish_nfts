#!/usr/bin/env python3
import os
import json
from pathlib import Path
import requests 
import tarfile
import asyncio
from os import listdir
from os.path import isfile, join, basename, exists, realpath, dirname
from db.sessions import dump_domains, add_domain
from typing import Optional, List
from fastapi import Depends
from api.dependencies.repositories import get_repository
from db.repositories.domains import DomainRepository
from db.schemas.domains import DomainAdd, DomainRead


script_path = realpath(dirname(__file__))

def get_domain_list():
    return dump_domains()


def files_in_folder(folder):
    return [f for f in listdir(folder) if isfile(join(folder, f))]


def create_list_folder(list_type):    
    Path(f"{script_path}/lists/{list_type}").mkdir(parents=True, exist_ok=True)


def extract_tar_url(url, extract_path, fn):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        print(f"{extract_path}/{fn}")
        with open(f"{extract_path}/{fn}", 'wb') as f:
            f.write(response.raw.read())
            with tarfile.open(f, mode="r:gz") as tf:
                tf.extractall(extract_path)


def get_text_file(link):
    data = requests.get(link)
    return data.text


def process_source_lists():
    with open(f"{script_path}/sources.json") as f:
        sources = json.load(f)
    for i in ["domains", "contracts"]:
        create_list_folder(i)
        for j in ["init", "cron"]:
            urls = sources[i][j]
            process_lists(i, urls, j == "cron")


def process_lists(list_type, urls, cron=True):
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
        print(f"Updated {url}")


def migrate_lists():
    known_domains = get_domain_list()
    if known_domains:
        print(f"{len(known_domains)} domains in the blocklist")
    for list_type in ["contracts", "domains"]:
        folder = f"{script_path}/lists/{list_type}"
        files = files_in_folder(folder)
        for file in files:
            if file.endswith(".txt"):
                with open(f"{folder}/{file}") as f:
                    domains = set([i.strip() for i in f.readlines()])
                    domains = domains - set(known_domains)
                    domains = [i.replace("http://", "").replace("http://", "") for i in domains]
                    for domain in domains:
                        if domain not in known_domains:
                            print(f"Adding {domain} from {file}...")
                            add_domain(domain, file, True)
            else:
                print(f"Skipping {file}, it is not a text file...")


if __name__ == '__main__':
    process_source_lists()
    migrate_lists()
