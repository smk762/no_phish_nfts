from uuid import UUID, uuid4

import pytest
from sqlmodel.ext.asyncio.session import AsyncSession

from db.errors import EntityDoesNotExist
from db.repositories.contracts import ContractRepository
from db.schemas.contracts import ContractPatch
from enums import NetworkEnum
from logger import logger


@pytest.mark.asyncio
async def test_create_contract(db_session: AsyncSession, create_contract):
    address = "test"
    source = "test"
    for network in [i.value for i in NetworkEnum]:
        contract = create_contract(address=address, network=network, source=source)
        repository = ContractRepository(db_session)
        db_contract = await repository.create(contract)
        assert db_contract.address == contract.address
        assert db_contract.network == contract.network
        assert isinstance(db_contract.id, UUID)


@pytest.mark.asyncio
async def test_get_contracts(db_session: AsyncSession, create_contract):
    address = "test"
    source = "test"
    for network in [i.value for i in NetworkEnum]:
        contract = create_contract(address=address, network=network, source=source)
        repository = ContractRepository(db_session)
        await repository.create(contract)
        db_contracts = await repository.list(network)
        assert isinstance(db_contracts, list)
        assert db_contracts[0].address == contract.address
        assert db_contracts[0].network == contract.network


@pytest.mark.asyncio
async def test_get_contract(db_session: AsyncSession, create_contract):
    address = "test"
    source = "test"
    network = "bsc"
    contract = create_contract(address=address, network=network, source=source)
    repository = ContractRepository(db_session)
    contract_created = await repository.create(contract)
    contract_db = await repository.get(address=contract_created.address)
    assert contract_created == contract_db


@pytest.mark.asyncio
async def test_get_contract_by_id_not_found(db_session: AsyncSession):
    repository = ContractRepository(db_session)
    with pytest.raises(expected_exception=EntityDoesNotExist):
        await repository.get(address="not existing address")


@pytest.mark.asyncio
async def test_update_contract(db_session: AsyncSession, create_contract):
    address = "test"
    source = "test"
    final_source = "test2"
    options = [i.value for i in NetworkEnum]
    init_network = options[-1]
    contract = create_contract(address=address, network=init_network, source=source)
    repository = ContractRepository(db_session)
    db_contract = await repository.create(contract)
    logger.info(f"Created {init_network}")
    for final_network in options[:-1]:
        update_contract = await repository.patch(
            contract_patch=ContractPatch(
                address=address, source=final_source, network=final_network
            ),
        )
        assert update_contract.network == final_network
        assert update_contract.source == final_source
        logger.info(f"Updated {init_network} to {final_network}")
        init_network = final_network
