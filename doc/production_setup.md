# Production Setup Guide

This document walks through bringing **No Phish NFTs** online on a brand-new Linux server (Ubuntu/Debian flavor). Adjust the commands to match your distribution, internal standards, and automation tooling.

---

## 1. Prepare the Host

1. Update system packages and reboot if the kernel changes:
   ```
   sudo apt update && sudo apt full-upgrade -y
   sudo reboot
   ```
2. Create a dedicated system user (optional but recommended):
   ```
   sudo adduser --disabled-login --gecos "" blocklist
   sudo usermod -aG sudo,docker blocklist
   ```
3. Harden SSH, enable automatic security updates, and configure UFW according to your policy. Only the reverse proxy and SSH ports should be exposed publicly; the stack binds to `127.0.0.1` by default.

## 2. Install Runtime Dependencies

```
sudo apt install -y ca-certificates curl gnupg lsb-release make git
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update && sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable docker && sudo systemctl start docker
```

> **UFW + Docker:** follow the [official guidance](https://docs.docker.com/network/iptables/) to ensure Docker does not bypass your firewall rules (e.g., configuring `DOCKER_OPTS="--iptables=false"` or equivalent nftables policy).

## 3. Clone the Repository

```
sudo mkdir -p /opt/no_phish_nfts
sudo chown blocklist:blocklist /opt/no_phish_nfts
sudo -u blocklist git clone https://github.com/smk762/no_phish_nfts.git /opt/no_phish_nfts
cd /opt/no_phish_nfts
```

Keep the working tree clean; production deployments should come from tested tags or pinned commits.

## 4. Create the Docker Network

The Compose file expects an external network named `nft-net`:

```
docker network create nft-net
```

If the network already exists (shared between environments), the command is idempotent.

## 5. Configure Environment Variables

Copy or create `/opt/no_phish_nfts/.env` and populate every key referenced in `core/config.py`:

- `TITLE`, `DESCRIPTION`
- `FASTAPI_PORT` (default 8000)
- `DEBUG` (`False` in production)
- `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD`, `POSTGRES_SERVER=pgsql_db`, `POSTGRES_PORT=5432`
- `VIEW_API_KEYS` and `EDIT_API_KEYS` (space-separated secrets)
- `ALCHEMY_API_KEY`, `GOOGLE_API_KEY`, `MNEMONICHQ_API_KEY`
- `CAMO_KEY` (long random string shared with `camo_rs`)
- `DOMAIN` (public host, no trailing slash, e.g. `https://phish-api.example.com`)

Persist this file in your secrets management system and restrict file permissions (`chmod 600 .env`).

## 6. Build and Pull Images

```
docker compose pull          # grabs upstream postgres base image
docker compose build --pull  # builds fastapi & camo images with the latest Python/Rust bases
```

Review the output for warnings, then optionally tag the resulting images in your registry.

## 7. Initialize the Database

The SQLModel metadata initializer **drops existing tables** before recreating them. Run it once on a fresh deployment:

```
docker compose run --rm fastapi_nft poetry run python create_tables.py
```

If you ever need to rerun it, back up the `db-postgres` volume first.

## 8. Seed Blocklists

Populate the local `lists/` cache and database tables with upstream sources:

```
docker compose run --rm fastapi_nft poetry run python update_lists.py
```

This step downloads large files (tarballs, yaml, json). Ensure outbound HTTPS access is available.

## 9. Start the Stack

```
docker compose up -d
docker compose ps
```

Both `fastapi_nft`, `camo_rs`, and `pgsql_db` should be healthy. Logs are available via `docker compose logs -f fastapi_nft` (FastAPI) and `docker compose logs -f camo_rs` (proxy).

## 10. Validate the Deployment

1. Port-forward or curl from the host:
   ```
   curl "http://127.0.0.1:${FASTAPI_PORT}/api/blocklist/domain/list"
   ```
   Expect HTTP 200 with JSON payload.
2. Verify the OpenAPI UI at `/docs` via SSH tunnel or reverse proxy.
3. Test camo:
   ```
   HEX_URL=$(printf 'https://example.org/logo.png' | xxd -p -c 256)
   curl "http://127.0.0.1:${FASTAPI_PORT}/url/decode/${HEX_URL}"
   ```
4. Confirm Postgres connections:
   ```
   docker compose exec pgsql_db psql -U ${POSTGRES_USER} -d ${POSTGRES_DB} -c '\dt'
   ```

## 11. Reverse Proxy & TLS

- Bind `FASTAPI_PORT` and `POSTGRES_PORT` to `127.0.0.1` (default) and expose the API via nginx/Traefik/Caddy with HTTPS.
- Proxy `/camo/` directly to `http://127.0.0.1:8081` and keep headers intact.
- Enforce rate limiting and API-key validation at the edge if clients are untrusted.

## 12. Recurring Jobs

Schedule the list updater and any backups from root’s crontab or systemd timers:

```
0 0 * * * cd /opt/no_phish_nfts && docker compose run --rm fastapi_nft poetry run python update_lists.py >> /var/log/no-phish-lists.log 2>&1
```

Consider a second cron to prune Docker artifacts and vacuum Postgres.

## 13. Backups & Persistence

- `db-postgres` volume → core blocklist data. Snapshot via `docker run --rm -v db-postgres:/var/lib/postgresql/data ...` or `pg_dump`.
- `lists/` folder → cached feeds; back it up if you want to avoid re-downloading large tarballs.
- `reported_spam.json` → user-generated reports; ensure the file is writable by the container user and included in backups.

## 14. Upgrades & Rollbacks

1. `git fetch --tags` and checkout the target release.
2. `docker compose build --pull` to incorporate base image patches.
3. Run migrations if schema changes were introduced.
4. `docker compose up -d --force-recreate`.
5. Roll back by checking out the previous tag and repeating the build/up steps.

## 15. Monitoring & Alerting

- Expose container metrics via Docker logging drivers or a sidecar (Fluent Bit, Promtail, etc.).
- Track FastAPI health through synthetic checks (e.g., `/api/blocklist/domain/list?limit=1`).
- Monitor disk usage of the Docker volumes and the `lists/` directory—feed archives can grow quickly.

---

Following the steps above yields a repeatable production deployment with clear hooks for automation, monitoring, and backups. Adapt the commands to your infrastructure-as-code stack (Ansible, Terraform, etc.) as needed.



