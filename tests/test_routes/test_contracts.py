from uuid import UUID

import pytest
from fastapi import status

from db.repositories.contracts import ContractRepository


@pytest.mark.asyncio
async def test_get_contracts(async_client):
    response = await async_client.get("/api/contracts/contracts")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 0


@pytest.mark.asyncio
async def test_create_contract(async_client, create_contract):
    contract = create_contract()
    response = await async_client.post(
        "/api/contracts/contracts", json=contract.dict()
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json()["amount"] == contract.amount
    assert response.json()["description"] == contract.description
    assert UUID(response.json()["id"])


@pytest.mark.asyncio
async def test_get_contract(async_client, create_contract):
    contract = create_contract()
    response_create = await async_client.post(
        "/api/contracts/contracts", json=contract.dict()
    )
    response = await async_client.get(
        f"/api/contracts/contracts/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["amount"] == contract.amount
    assert response.json()["description"] == contract.description
    assert response.json()["id"] == response_create.json()["id"]


@pytest.mark.asyncio
async def test_delete_contract(async_client, create_contract):
    contract = create_contract()
    response_create = await async_client.post(
        "/api/contracts/contracts", json=contract.dict()
    )
    response = await async_client.delete(
        f"/api/contracts/contracts/{response_create.json()['id']}"
    )

    assert response.status_code == status.HTTP_204_NO_CONTENT


@pytest.mark.asyncio
async def test_update_contract(async_client, create_contract):
    contract = create_contract(amount=10, description="Init Description")
    response_create = await async_client.post(
        "/api/contracts/contracts", json=contract.dict()
    )

    new_amount = 20
    new_description = "New Description"
    response = await async_client.put(
        f"/api/contracts/contracts/{response_create.json()['id']}",
        json={"amount": new_amount, "description": new_description},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["amount"] == new_amount
    assert response.json()["description"] == new_description
    assert response.json()["id"] == response_create.json()["id"]


@pytest.mark.asyncio
async def test_get_contract_paginated(db_session, async_client, create_contracts):
    repository = ContractRepository(db_session)
    for contract in create_contracts(_qty=4):
        await repository.create(contract)

    response_page_1 = await async_client.get("/api/contracts/contracts?limit=2")
    assert len(response_page_1.json()) == 2

    response_page_2 = await async_client.get(
        "/api/contracts/contracts?limit=2&offset=2"
    )
    assert len(response_page_2.json()) == 2

    response = await async_client.get("/api/contracts/contracts")
    assert len(response.json()) == 4
