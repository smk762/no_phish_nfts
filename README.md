# No Phish NFTs

FastAPI + PostgreSQL service for checking if domains or NFT contract addresses appear on curated blocklists. The project also ships a `camo-rs` proxy for serving images/audio/video from untrusted origins and helper scripts for synchronising external threat feeds.

## Overview

- REST API for scanning domains and EVM/Solana NFT contracts against the local blocklist.
- Authenticated CRUD endpoints for maintaining the local lists via API keys.
- Camo encode/decode routes backed by the bundled `camo-rs` Rust reverse proxy.
- Data ingestion utility (`update_lists.py`) pulls from community feeds (Google Safe Browsing, Alchemy, MetaMask, Phantom, Mitchell Krogza, etc.) and merges custom entries.
- Test suite (pytest + httpx) and linting targets (black + isort) wired through Docker/Poetry.

## Architecture

| Component | Description |
| --- | --- |
| `fastapi_nft` | Python 3.10 container serving the FastAPI app (see `main.py`). Runs with Poetry-managed dependencies. |
| `pgsql_db` | PostgreSQL 14 instance storing `domains` and `contracts` tables (via SQLModel). |
| `camo_rs` | Rust-based content proxy translating hex-encoded URLs to media responses. |
| `update_lists.py` | CLI script used for seeding/refreshing blocklists and ingesting third-party feeds. |
| `lists/` | Local cache of downloaded feeds plus `custom.json` overrides for contracts and domains. |

## Requirements

- Docker Engine 20.10+ and the Docker Compose plugin (`docker compose` CLI). Configure Docker to start on boot and harden iptables/UFW according to your security policy.
- GNU Make (used by the convenience targets in `Makefile`).
- 20 GB+ free disk (feeds + Docker volumes).
- Optional: Poetry ≥ 1.5.0 and Python ≥ 3.10 if you want to run/test outside Docker.
- API keys for Alchemy, Google Safe Browsing, and MnemonicHQ plus internal API keys for authenticated routes.

## Configuration

All configuration lives in `.env`. Every variable maps 1:1 to `core/config.py` or Docker Compose fields:

| Key | Purpose |
| --- | --- |
| `TITLE`, `DESCRIPTION` | Metadata for the generated OpenAPI docs. |
| `FASTAPI_PORT` | Port FastAPI listens on inside/outside the container. |
| `DEBUG` | `"True"` enables SQL echo logging. |
| `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` | Database credentials interpolated into connection URLs. |
| `POSTGRES_SERVER`, `POSTGRES_PORT` | Hostname/port for PostgreSQL (use `pgsql_db` when using Docker Compose). |
| `VIEW_API_KEYS`, `EDIT_API_KEYS` | Space-delimited API keys. Edit-only routes require a key from `EDIT_API_KEYS`. |
| `ALCHEMY_API_KEY`, `GOOGLE_API_KEY`, `MNEMONICHQ_API_KEY` | Third-party credentials for feed enrichment. |
| `CAMO_KEY` | Shared secret between FastAPI and `camo-rs` for signing proxy requests. |
| `DOMAIN` | Public base URL (without trailing slash) used when building camo proxy URLs. |

Minimal example:

```
TITLE="No Phish NFTs"
DESCRIPTION="Domain & NFT contract blocklist API"
FASTAPI_PORT=8000
DEBUG=False
POSTGRES_DB=blocklist
POSTGRES_USER=blocklist
POSTGRES_PASSWORD=supersecret
POSTGRES_SERVER=pgsql_db
POSTGRES_PORT=5432
VIEW_API_KEYS="viewer_key"
EDIT_API_KEYS="editor_key another_editor"
ALCHEMY_API_KEY="alchemy_key"
GOOGLE_API_KEY="google_key"
MNEMONICHQ_API_KEY="mnemonic_key"
CAMO_KEY="choose-a-long-random-string"
DOMAIN="https://example.org"
```

## Getting Started with Docker

1. **Clone the project**
   ```
   git clone https://github.com/smk762/no_phish_nfts.git
   cd no_phish_nfts
   ```
2. **Create the shared Docker network** (Compose expects `nft-net` to exist):
   ```
   docker network create nft-net
   ```
3. **Add your `.env`** (see template above) and ensure `reported_spam.json` is writable (the `report` endpoint appends to it).
4. **Build and run**  
   - `make dev` → foreground `docker compose up --build`  
   - `make run` → rebuild, start in the background, then tail logs  
   - `make down` → stop and remove containers
5. **Initialize the database** (destructive – drops existing tables):
   ```
   docker compose run --rm fastapi_nft poetry run python create_tables.py
   ```
6. **Seed blocklists** (downloads feeds into `lists/` and syncs DB):
   ```
   docker compose run --rm fastapi_nft poetry run python update_lists.py
   ```
7. **Access the API** at `http://localhost:${FASTAPI_PORT}/docs` or the raw endpoints under `/api/blocklist/...`. Camo routes live under `/url/encode` and `/url/decode`.

## Make Targets

- `make dev` – iterate locally with live logs.  
- `make run` – rebuild, run detached, and tail logs (default workflow).  
- `make stop` / `make down` – stop or tear down the stack.  
- `make shell` – open a shell in the FastAPI container.  
- `make logs` – tail combined service logs.  
- `make tests` / `make lint` – execute pytest or code-style checks inside the container.

## Maintaining Blocklists

- `sources.json` specifies upstream feeds (`init` runs once; `cron` entries overwrite every run). Update this file to add/remove feeds.
- `lists/contracts/custom.json` and `lists/contracts/nft-blocklist.yaml` (plus domain equivalents) hold custom additions. Anything under `lists/**/custom.json` remains untouched by the sync job.
- Run `docker compose run --rm fastapi_nft poetry run python update_lists.py` manually or schedule it (see **Crons** below) to refresh entries. The script:
  - Pulls files into `lists/<type>/`.
  - Normalizes and deduplicates entries before inserting via SQLModel.
  - Enriches from Alchemy spam contracts and Google Safe Browsing if a requested domain is missing.

## Testing & Linting

```
make tests  # pytest + httpx integration tests
make lint   # black + isort (runs inside the FastAPI container)
```

For local runs without Docker:

```
poetry install
poetry run pytest
poetry run python create_tables.py
```

Ensure your local Postgres matches the `.env` settings (`POSTGRES_SERVER=localhost` etc.).

## API Summary

| Method | Path | Description | Notes |
| --- | --- | --- | --- |
| `GET` | `/api/blocklist/domain/list` | Paginated domain blocklist. | `limit` ≤ 100, `offset` supported. |
| `POST` | `/api/blocklist/domain/scan` | Check one or more comma-delimited domains. | Automatically queries Google Safe Browsing when missing. |
| `POST` | `/api/blocklist/domain/create` | Add a domain. | Requires `X-API-Key` from `EDIT_API_KEYS`. |
| `PUT` | `/api/blocklist/domain/update` | Update `source`/metadata. | Requires edit key. |
| `DELETE` | `/api/blocklist/domain/delete?url=...` | Remove a domain. | Requires edit key. |
| `GET` | `/api/blocklist/contract/{network}/list` | Paginated contract blocklist per network. | Networks from `NetworkEnum` (eth, polygon, avalanche, bsc, fantom, solana). |
| `POST` | `/api/blocklist/contract/scan` | Bulk-check comma-delimited contract addresses. | Validates requested network. |
| `POST` | `/api/blocklist/contract/create` | Add a contract entry. | Requires edit key. |
| `PUT` | `/api/blocklist/contract/update` | Update contract metadata. | Requires edit key. |
| `DELETE` | `/api/blocklist/contract/delete` | Delete a contract entry. | Requires `network` + `contract_address` query params and edit key. |
| `POST` | `/api/blocklist/contract/report` | Report a suspicious contract. | Stores reporter wallet per network in `reported_spam.json`. |
| `POST` | `/api/blocklist/contract/view_reported` | View accumulated reports. | Read-only. |
| `GET` | `/url/decode/{hex}` | Proxy signed hex URLs through `camo-rs`. | Requires correct `CAMO_KEY`/`DOMAIN`. |
| `POST` | `/url/encode/{url}` | Encode a URL to hex for use with the proxy. | Accepts full URL string. |

> Wallet scanning endpoints (`api/routes/addresses.py`) remain disabled by default. Uncomment the include in `api/router.py` if you need MnemonicHQ wallet scans.

## Camo Encode/Decode Notes

- `CAMO_KEY` must match in `.env` and the `camo_rs` container environment.
- `DOMAIN` should point to the public domain serving the proxy (no trailing slash). The FastAPI route calculates `https://<DOMAIN>/camo/<hmac>/<hex>`.
- `camo-rs` listens on `127.0.0.1:8081` by default. Front it with your preferred reverse proxy to expose `/camo/`.
- See `camo-rs/docs/*.md` for upstream configuration details.

## Crons / Automation

Example cron entry (runs lists sync daily at midnight from the project root):

```
0 0 * * * cd /home/user/no_phish_nfts && docker compose run --rm fastapi_nft poetry run python update_lists.py >> /var/log/no-phish-lists.log 2>&1
```

Ensure the cron user has access to Docker and the project files.

## Production Deployment

For a hardened step-by-step guide (installing Docker, preparing the host, seeding data, wiring reverse proxies, backups, etc.) see `doc/production_setup.md`.

## Visual References

<p align="center" width="100%">
    <img src="doc/img/endpoints.png" width="800px" alt="Endpoints overview" />
</p>

<p align="center" width="100%">
    <a href="https://www.postgresql.org/" style="margin:20px">
        <img src="doc/img/postgresql.png" height="100" alt="PostgreSQL" />
    </a>
    <a href="https://fastapi.tiangolo.com/" style="margin:20px">
        <img src="doc/img/fastapi.png" height="100" alt="FastAPI" /> 
    </a>
    <a href="https://www.docker.com/" style="margin:20px">
        <img src="doc/img/docker.png" height="100" alt="Docker" />
    </a>
</p>

<p align="center" width="100%">
    <a href="https://metamask.io/" style="margin:20px">
        <img src="doc/img/metamask.jpg" height="60" alt="Metamask" />
    </a>
    <a href="https://developers.google.com/safe-browsing" style="margin:20px">
        <img src="doc/img/google-sb.png" height="60" alt="Google Safe Browsing" /> 
    </a>
    <a href="https://www.alchemy.com/" style="margin:20px">
        <img src="doc/img/alchemy.png" height="60" alt="Alchemy" />
    </a>
    <a href="https://www.mnemonichq.com/" style="margin:20px">
        <img src="doc/img/mnemonic.png" height="60" alt="MnemonicHQ" />
    </a>
    <a href="https://github.com/mitchellkrogza/Phishing.Database" style="margin:20px">
        <img src="doc/img/phishing-logo.jpg" height="60" alt="Mitchell Krogza Phishing DB" />
    </a>
    <a href="https://github.com/phantom/blocklist" style="margin:20px">
        <img src="doc/img/phantom.png" height="60" alt="Phantom" />
    </a>
</p>

## License

Apache-2.0 (see `LICENCE`).