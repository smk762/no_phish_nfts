# No Phish NFTs

This repo serves an API to check if a domain or contract address has been identified as spam or otherwise malicious.

## Endpoints

[GET] `blocklist/contract/{network}/{address}` - Returns `true` (if contract is in block list) or `false`
[GET] `blocklist/domain/{domain}` - Returns `true` (if domain is in block list) or `false`
[GET] `blocklist/{network}/contract_list` - Returns the NFT contracts blocklist for a network
[GET] `blocklist/domain_list` - Returns domain blocklist

[POST] `blocklist/add_domain/{domain}` - Requires authentication. Adds a new domain to the domain block list.
[POST] `blocklist/add_contract/{network}/{address}` - Requires authentication. Adds a new contract to the NFT contracts block list.


## Stack

FastAPI
PGSQL
Docker

---
## Setup

### Requirements

 - [Docker](https://docs.docker.com/engine/install/ubuntu/) / [w/ convenience script](https://docs.docker.com/engine/install/ubuntu/#install-using-the-convenience-script)
 - [Docker Compose](https://docs.docker.com/compose/install/linux/#install-using-the-repository)
 - Docker linux post install steps: https://docs.docker.com/engine/install/linux-postinstall/ , Configure Docker to start on boot with systemd
 - 20GB+ disk space free
 - [PgSQL Dependencies] `sudo apt install libpq-dev`
 - [Poetry](https://python-poetry.org/) python dependency management tool


### Make Docker respect UFW

**Docker adds iptables rules that will override UFW rules!** 
Make sure to run the steps below to secure the ports used by Docker. See this article for more info: https://www.techrepublic.com/article/how-to-fix-the-docker-and-ufw-security-flaw/

Open docker config file
```
sudo nano /etc/default/docker
```

Add this line; save and exit.
```
DOCKER_OPTS="--iptables=false"
```

Restart docker
```
sudo systemctl restart docker
```
---

### Install API

- Clone repo `git clone https://github.com/smk762/no_phish_nfts`
- Create network for project with `docker network create nft-net`
- Copy `.env.example` to `.env` and populate with required environment variables
- Run `poetry install` to install dependencies
- Run `docker compose build` to build the containers
- Run `docker compose up -d` to run the containers as a daemon
- Run `docker compose logs -f --tail 33` to view runtime logs


## Crons

- Add block list sources to `sources.json`
- Add custom entries in `lists/*/custom.json`
- Setup a crontab entry like `0 0 * * * poetry run /home/user/no_phish_nfts/update_lists.py` to refresh the lists every 24 hours at midnight.
