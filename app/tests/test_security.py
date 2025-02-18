import pytest
from unittest import mock
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from jose import jwt
from datetime import datetime, timedelta, timezone
from ..security import get_current_user, SECRET_KEY, ALGORITHM
from ..models import schemas


@pytest.fixture
def db_session():
    return mock.MagicMock(spec=Session)


@pytest.fixture
def token_data():
    return {
        "sub": "test_user_id",
        "exp": (datetime.now(timezone.utc) + timedelta(minutes=30)).timestamp()
    }


@pytest.fixture
def valid_token(token_data):
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


@pytest.fixture
def expired_token(token_data):
    token_data["exp"] = (
        datetime.now(timezone.utc) - timedelta(minutes=30)
    ).timestamp()
    return jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)


def test_get_current_user_valid_token(db_session, valid_token):
    user = schemas.Customer(
        id="test_user_id",
        name="Test User",
        email="test@example.com")
    db_session.query.return_value.filter.return_value.first.return_value = user

    with mock.patch('app.services.repository.get_customer', return_value=user):
        result = get_current_user(db_session, valid_token)

    assert result == user


def test_get_current_user_invalid_token(db_session):
    invalid_token = "invalid_token"
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(db_session, invalid_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Credenciais inválidas ou expiradas"


def test_get_current_user_expired_token(db_session, expired_token):
    with pytest.raises(HTTPException) as excinfo:
        get_current_user(db_session, expired_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Credenciais inválidas ou expiradas"


def test_get_current_user_user_not_found(db_session, valid_token):
    db_session.query.return_value.filter.return_value.first.return_value = None

    with mock.patch('app.services.repository.get_customer', return_value=None):
        with pytest.raises(HTTPException) as excinfo:
            get_current_user(db_session, valid_token)
    assert excinfo.value.status_code == status.HTTP_401_UNAUTHORIZED
    assert excinfo.value.detail == "Credenciais inválidas ou expiradas"
