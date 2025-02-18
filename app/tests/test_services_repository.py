import pytest
from unittest import mock
from sqlalchemy.orm import Session
from unittest.mock import MagicMock
from ..models import schemas
from ..services.repository import (
    create_customer,
    create_anonymous_customer,
    create_user
)


@pytest.fixture
def db_session():
    return mock.MagicMock(spec=Session)


def customer_data():
    return schemas.CustomerCreate(
        name="Test Customer",
        email="test@example.com",
        cpf="12345678900"
    )


def test_create_customer(db_session, customer_data):
    # Mock the add, commit, and refresh methods
    db_session.add = mock.MagicMock()
    db_session.commit = mock.MagicMock()
    db_session.refresh = mock.MagicMock()

    # Call the function to test
    created_customer = create_customer(db_session, customer_data)

    # Assertions
    db_session.add.assert_called_once()
    db_session.commit.assert_called_once()
    db_session.refresh.assert_called_once_with(created_customer)
    assert created_customer.name == customer_data.name
    assert created_customer.email == customer_data.email
    assert created_customer.cpf == customer_data.cpf


def test_create_anonymous_customer():
    # Mock the database session
    db = MagicMock(spec=Session)

    # Mock the Customer model
    db.add.return_value = None
    db.commit.return_value = None
    db.refresh.return_value = None

    # Call the function to test
    result = create_anonymous_customer(db)

    # Assertions
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once()
    assert result.name == 'Anonymous'
    assert result.email is None
    assert result.cpf is None
    assert result.hashed_password is None


def test_create_user(db_session):
    user_data = schemas.CustomerCreate(
        name="Test User",
        email="test@example.com",
        cpf="12345678900",
        password="password123"
    )

    with mock.patch(
        'app.services.repository.security.get_password_hash',
        return_value="hashed_password"
    ):
        user = create_user(db_session, user_data)

    # Assertions
    assert user.name == user_data.name
    assert user.email == user_data.email
    assert user.cpf == user_data.cpf
    assert user.hashed_password == "hashed_password"
