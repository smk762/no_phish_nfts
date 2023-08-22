import pytest
from pydantic import ValidationError

from db.schemas.contracts import ContractCreate
from logger import logger

def test_contract_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate()


def test_contract_instance_network_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(address="test", network="polygon")


def test_contract_instance_address_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(source="source", network="polygon")


def test_contract_instance_source_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(address="test", network="polygon")


def test_contract_instance_network_wrong():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(address="test", network="test", source="source")


def test_contract_instance_address_wrong():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(address=5, network="test", source="source")


def test_contract_instance_source_wrong():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(address="test", network="test", source=5)


