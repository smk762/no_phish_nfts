import pytest
from pydantic import ValidationError

from db.schemas.domains import DomainCreate


def test_domain_instance_empty():
    with pytest.raises(expected_exception=ValidationError):
        DomainCreate()


def test_domain_instance_amount_empty():
    with pytest.raises(expected_exception=ValidationError):
        DomainCreate(description="Description")


def test_domain_instance_description_empty():
    with pytest.raises(expected_exception=ValidationError):
        DomainCreate(amount=10)


def test_domain_instance_amount_wrong():
    with pytest.raises(expected_exception=ValidationError):
        DomainCreate(amount="amount", description="Description")
