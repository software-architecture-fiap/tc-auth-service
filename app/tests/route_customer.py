import pytest
from fastapi import status
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from types import SimpleNamespace
from ..main import app
from ..models import schemas

client = TestClient(app)
CUSTOMER_EMAIL = "customer@fiap.com.br"
CUSTOMER_NAME = "Customer Name"
CUSTOMER_PASSWORD = "password123"


@pytest.fixture
def mock_db_session():
    """Mocked database session for tests"""
    return MagicMock()


@pytest.fixture
def mock_user():
    """Mocked user for tests"""
    return SimpleNamespace(
        id=1,
        email="admin@fiap.com.br",
        hashed_password=(
            "$2b$12$wU3o3gQxELZfiMjri7FxNODcDbUGbeLy8wPOpvpb1JHxH33jWrxvq"
        )
    )


@pytest.fixture
def mock_customer():
    """Mocked customer for tests"""
    return schemas.Customer(
        email=CUSTOMER_EMAIL,
        name=CUSTOMER_NAME
    )


def test_create_customer(mocker, mock_db_session, mock_customer):
    """Test creating a new customer"""
    mocker.patch(
        "app.services.repository.get_user_by_email",
        return_value=None
    )
    mocker.patch(
        "app.services.repository.create_user",
        return_value=mock_customer
    )

    customer_data = {
        "name": CUSTOMER_NAME,
        "password": CUSTOMER_PASSWORD
    }
    response = client.post("/admin", json=customer_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == mock_customer.email


def test_create_customer_existing_email(
    mocker, mock_db_session, mock_customer):
    """Test creating a customer with an existing email"""
    mocker.patch(
        "app.services.repository.get_user_by_email",
        return_value=mock_customer
    )

    customer_data = {
        "email": CUSTOMER_EMAIL,
        "name": CUSTOMER_NAME,
        "password": CUSTOMER_PASSWORD
    }
    response = client.post("/admin", json=customer_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()["detail"] == "E-mail já registrado"


def test_get_customers(mocker, mock_db_session, mock_customer):
    """Test retrieving a list of customers"""
    mocker.patch(
        "app.services.repository.get_customers",
        return_value=[mock_customer]
    )

    response = client.get("/")

    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) == 1
    assert response.json()[0]["email"] == mock_customer.email


def test_check_customer(mocker, mock_db_session, mock_customer):
    """Test identifying a customer by CPF"""
    mocker.patch(
        "app.services.repository.get_customer_by_cpf",
        return_value=mock_customer
    )

    cpf_data = {"cpf": "12345678900"}
    response = client.post("/identify", json=cpf_data)

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == mock_customer.email


def test_check_customer_not_found(mocker, mock_db_session):
    """Test identifying a customer by CPF not found"""
    mocker.patch(
        "app.services.repository.get_customer_by_cpf",
        return_value=None
    )

    cpf_data = {"cpf": "12345678900"}
    response = client.post("/identify", json=cpf_data)

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Cliente não encontrado"


def test_create_anonymous_customer(mocker, mock_db_session, mock_customer):
    """Test creating an anonymous customer"""
    mocker.patch(
        "app.services.repository.create_anonymous_customer",
        return_value=mock_customer
    )

    response = client.post("/anonymous")

    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == mock_customer.email