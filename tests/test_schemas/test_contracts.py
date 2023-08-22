import pytest
from pydantic import ValidationError

from db.schemas.contracts import ContractCreate


def test_contract_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate()


def test_contract_instance_amount_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(description="Description")


def test_contract_instance_description_empty():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(amount=10)


def test_contract_instance_amount_wrong():
    with pytest.raises(expected_exception=ValidationError):
        ContractCreate(amount="amount", description="Description")
