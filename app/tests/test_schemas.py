import pytest
from pydantic import ValidationError
from ..models.schemas import Customer


def test_customer_creation():
    customer_data = {
        "id": 1,
        "name": "John Doe",
        "email": "john.doe@example.com",
        "cpf": "12345678900"
    }
    customer = Customer(**customer_data)
    assert customer.id == 1
    assert customer.name == "John Doe"
    assert customer.email == "john.doe@example.com"
    assert customer.cpf == "12345678900"


def test_customer_missing_id():
    customer_data = {
        "name": "John Doe",
        "email": "john.doe@example.com",
        "cpf": "12345678900"
    }
    with pytest.raises(ValidationError):
        Customer(**customer_data)


def test_customer_optional_fields():
    customer_data = {
        "id": 1
    }
    customer = Customer(**customer_data)
    assert customer.id == 1
    assert customer.name is None
    assert customer.email is None
    assert customer.cpf is None
