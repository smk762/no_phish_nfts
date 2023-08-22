from uuid import UUID, uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from db.errors import EntityDoesNotExist
from db.repositories.contracts import ContractRepository
from db.schemas.contracts import ContractPatch


@pytest.mark.asyncio
async def test_create_contract(db_session: AsyncSession, create_contract):
    contract = create_contract()
    repository = ContractRepository(db_session)

    db_contract = await repository.create(contract)

    assert db_contract.address == contract.address
    assert db_contract.network == contract.network
    assert isinstance(db_contract.id, UUID)


@pytest.mark.asyncio
async def test_get_contracts(db_session: AsyncSession, create_contract):
    contract = create_contract()
    repository = ContractRepository(db_session)
    await repository.create(contract)

    db_contracts = await repository.list("polygon")

    assert isinstance(db_contracts, list)
    assert db_contracts[0].address == contract.address
    assert db_contracts[0].network == contract.network


@pytest.mark.asyncio
async def test_get_contract_by_id(db_session: AsyncSession, create_contract):
    contract = create_contract()
    repository = ContractRepository(db_session)

    contract_created = await repository.create(contract)
    contract_db = await repository.get(contract_id=contract_created.id)

    assert contract_created == contract_db


@pytest.mark.asyncio
async def test_get_contract_by_id_not_found(db_session: AsyncSession):
    repository = ContractRepository(db_session)

    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(contract_id=uuid4())


@pytest.mark.asyncio
async def test_update_contract(db_session: AsyncSession, create_contract):
    init_address = "0x4d2d94b07b9d8ac2964aa27726ff20e8a67e780a"
    init_network = "polygon"
    final_address = "0x4d2d94b07b9d8ac2964aa27726ff20e8a67e780a"
    final_network = "eth"
    contract = create_contract(address=init_address, network=init_network)
    repository = ContractRepository(db_session)
    db_contract = await repository.create(contract)

    update_contract = await repository.patch(
        contract_id=db_contract.id,
        contract_patch=ContractPatch(
            address=final_address, network=final_network
        ),
    )

    assert update_contract.id == db_contract.id
    assert update_contract.address == final_address
    assert update_contract.network == final_network


@pytest.mark.asyncio
async def test_soft_delete_contract(db_session: AsyncSession, create_contract):
    contract = create_contract()
    repository = ContractRepository(db_session)
    db_contract = await repository.create(contract)

    delete_contract = await repository.delete(contract_id=db_contract.id)

    assert delete_contract is None
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(contract_id=db_contract.id)
