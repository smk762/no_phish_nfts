
dev:
	@docker compose -f docker-compose.yml up --build

run:
	@docker compose -f docker-compose.yml stop
	@docker compose -f docker-compose.yml up --build -d
	@docker compose -f ./docker-compose.yml logs -f --tail 33

stop:
	@docker compose -f docker-compose.yml stop

down:
	@docker compose -f ./docker-compose.yml down --remove-orphans

logs:
	@docker compose -f ./docker-compose.yml logs -f --tail 33

shell: run
	@docker exec -it fastapi_nft bash

tests: run
	@docker exec -it fastapi_nft poetry run pytest

lint: run
	@docker exec -it fastapi_nft poetry run black .
	@docker exec -it fastapi_nft poetry run isort . --profile black

.PHONY: dev run stop down logs shell tests lint
