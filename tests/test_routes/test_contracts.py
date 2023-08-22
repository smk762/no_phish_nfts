from uuid import UUID

import pytest
from fastapi import status

from core.config import settings
from db.repositories.contracts import ContractRepository
from enums import NetworkEnum
from logger import logger


@pytest.mark.asyncio
async def test_get_contracts(async_client):
    for network in [i.value for i in NetworkEnum]:
        url = f"/contract/{network}/list"
        logger.info(url)
        response = await async_client.get(url)
        logger.info(response.json())
        logger.info(response.text)
        logger.info(response)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_create_and_delete_contract(async_client, create_contract):
    for network in [i.value for i in NetworkEnum]:
        contract = create_contract("test contract", network, "test")
        url = f"/contract/create"
        response = await async_client.post(url, json=contract.dict())
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        headers = {
            "X-API-Key": settings.valid_api_keys["edit"][0],
            "accept": "application/json",
        }
        response = await async_client.post(url, json=contract.dict(), headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.json()["address"] == contract.address
        assert response.json()["network"] == contract.network
        assert response.json()["source"] == contract.source
        address = "test contract"
        url = f"/contract/delete?network={network}&contract_address={address}"
        response = await async_client.delete(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        headers = {
            "X-API-Key": settings.valid_api_keys["edit"][0],
            "accept": "application/json",
        }
        response = await async_client.delete(url, headers=headers)
        assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_get_contract(async_client, create_contract):
    for network in [i.value for i in NetworkEnum]:
        url = f"/contract/create"
        contract = create_contract(
            address="test contract", network=network, source="test"
        )
        headers = {
            "X-API-Key": settings.valid_api_keys["edit"][0],
            "accept": "application/json",
        }
        response = await async_client.post(url, json=contract.dict(), headers=headers)
        assert response.status_code == status.HTTP_201_CREATED
        response = await async_client.get(f"/contract/{network}/list")
        assert response.status_code == status.HTTP_200_OK
        assert response.json()[0]["address"] == contract.address
        assert response.json()[0]["network"] == contract.network
        assert response.json()[0]["source"] == contract.source


@pytest.mark.asyncio
async def test_update_contract(async_client, create_contract):
    address = "test_update"
    old_source = "old_source"
    new_source = "new_source"
    headers = {
        "X-API-Key": settings.valid_api_keys["edit"][0],
        "accept": "application/json",
    }

    network = "polygon"
    contract = create_contract(address=address, network=network, source="old_source")
    response = await async_client.post(
        "/contract/create", json=contract.dict(), headers=headers
    )
    logger.info(response.json())
    body = {"address": address, "source": new_source, "network": network}
    logger.debug(f"body: {body}")
    response = await async_client.put(f"/contract/update", headers=headers, json=body)
    logger.info(response.json())
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["address"] == address
    assert response.json()["network"] == network
    assert response.json()["source"] == new_source
