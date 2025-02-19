import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, validates
from ..database.database import Base
from ..models.models import Customer
import re

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


@validates('email')
def validate_email(self, key, address):
    if not re.match(r"[^@]+@[^@]+\.[^@]+", address):
        raise ValueError("Invalid email address")
    return address


@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_create_customer(test_db):
    new_customer = Customer(
        name="John Doe",
        email="john.doe@example.com",
        cpf="12345678900",
        hashed_password="hashed_password"
    )
    test_db.add(new_customer)
    test_db.commit()
    test_db.refresh(new_customer)

    assert new_customer.id is not None
    assert new_customer.name == "John Doe"
    assert new_customer.email == "john.doe@example.com"
    assert new_customer.cpf == "12345678900"
    assert new_customer.hashed_password == "hashed_password"


def test_read_customer(test_db):
    customer = test_db.query(Customer).filter(
        Customer.email == "john.doe@example.com"
    ).first()
    assert customer is not None
    assert customer.name == "John Doe"
    assert customer.email == "john.doe@example.com"
    assert customer.cpf == "12345678900"


def test_update_customer(test_db):
    customer = test_db.query(Customer).filter(
        Customer.email == "john.doe@example.com"
    ).first()
    customer.name = "Jane Doe"
    test_db.commit()
    test_db.refresh(customer)

    assert customer.name == "Jane Doe"


def test_delete_customer(test_db):
    customer = test_db.query(Customer).filter(
        Customer.email == "john.doe@example.com"
    ).first()
    test_db.delete(customer)
    test_db.commit()

    customer = test_db.query(Customer).filter(
        Customer.email == "john.doe@example.com"
    ).first()
    assert customer is None
