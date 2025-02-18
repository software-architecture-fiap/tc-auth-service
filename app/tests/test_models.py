import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from ..database.database import Base
from ..models.models import Customer

# Setup the test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


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


def test_create_customer_with_invalid_email(test_db):
    new_customer = Customer(
        name="Invalid Email",
        email="invalid-email",
        cpf="12345678901",
        hashed_password="hashed_password"
    )
    test_db.add(new_customer)
    with pytest.raises(Exception):
        test_db.commit()


def test_create_customer_with_duplicate_email(test_db):
    customer1 = Customer(
        name="Customer One",
        email="duplicate@example.com",
        cpf="12345678902",
        hashed_password="hashed_password1"
    )
    customer2 = Customer(
        name="Customer Two",
        email="duplicate@example.com",
        cpf="12345678904",
        hashed_password="hashed_password2"
    )
    test_db.add(customer1)
    test_db.commit()
    test_db.refresh(customer1)

    with pytest.raises(Exception):
        test_db.add(customer2)
        test_db.commit()


def test_create_customer_with_duplicate_cpf(test_db):
    customer1 = Customer(
        name="Customer One",
        email="unique1@example.com",
        cpf="12345678904",
        hashed_password="hashed_password1"
    )
    customer2 = Customer(
        name="Customer Two",
        email="unique2@example.com",
        cpf="12345678903",
        hashed_password="hashed_password2"
    )
    test_db.add(customer1)
    test_db.commit()
    test_db.refresh(customer1)

    with pytest.raises(Exception):
        test_db.add(customer2)
        test_db.commit()


def test_create_customer_with_missing_fields(test_db):
    new_customer = Customer(
        name=None,
        email=None,
        cpf=None,
        hashed_password=None
    )
    with pytest.raises(Exception):
        test_db.add(new_customer)
        test_db.commit()
