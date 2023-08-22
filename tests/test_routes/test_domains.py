from uuid import UUID

import pytest
from fastapi import status

from core.config import settings
from db.repositories.domains import DomainRepository
from enums import NetworkEnum
from logger import logger


@pytest.mark.asyncio
async def test_get_domains(async_client):
    url = f"/domain/list"
    logger.info(url)
    response = await async_client.get(url)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_create_and_delete_domain(async_client, create_domain):
    test_url = "test.domain"
    domain = create_domain(url=test_url, source="test")
    url = f"/domain/create"
    response = await async_client.post(url, json=domain.dict())
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    headers = {
        "X-API-Key": settings.valid_api_keys["edit"][0],
        "accept": "application/json",
    }
    response = await async_client.post(url, json=domain.dict(), headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["url"] == domain.url
    assert response.json()["source"] == domain.source
    url = f"/domain/delete?url={test_url}"
    response = await async_client.delete(url)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    headers = {
        "X-API-Key": settings.valid_api_keys["edit"][0],
        "accept": "application/json",
    }
    response = await async_client.delete(url, headers=headers)
    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_domain(async_client, create_domain):
    url = f"/domain/create"
    domain = create_domain(url="test.domain", source="test")
    headers = {
        "X-API-Key": settings.valid_api_keys["edit"][0],
        "accept": "application/json",
    }
    response = await async_client.post(url, json=domain.dict(), headers=headers)
    assert response.status_code == status.HTTP_201_CREATED
    response = await async_client.get(f"/domain/list")
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]["url"] == domain.url
    assert response.json()[0]["source"] == domain.source


@pytest.mark.asyncio
async def test_update_domain(async_client, create_domain):
    old_url = "old.url"
    new_url = "new.url"
    old_source = "old_source"
    new_source = "new_source"
    headers = {
        "X-API-Key": settings.valid_api_keys["edit"][0],
        "accept": "application/json",
    }
    domain = create_domain(url=old_url, source=old_source)
    response = await async_client.post(
        "/domain/create", json=domain.dict(), headers=headers
    )
    logger.info(response.json())
    body = {"url": new_url, "source": new_source}
    logger.debug(f"body: {body}")
    response = await async_client.put(f"/domain/update", headers=headers, json=body)
    logger.info(response.json())
    assert response.status_code == status.HTTP_404_NOT_FOUND
    body = {"url": old_url, "source": new_source}
    logger.debug(f"body: {body}")
    response = await async_client.put(f"/domain/update", headers=headers, json=body)
    logger.info(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["url"] == old_url
    assert response.json()["source"] == new_source
