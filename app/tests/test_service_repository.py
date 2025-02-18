import pytest
from unittest import mock
from sqlalchemy.orm import Session
from app.models import models
from app.services.repository import create_admin_user


@pytest.fixture
def db_session():
    return mock.Mock(spec=Session)


@pytest.fixture
def mock_env_vars(monkeypatch):
    monkeypatch.setenv('ADMIN_EMAIL', 'admin@example.com')
    monkeypatch.setenv('ADMIN_PASSWORD', 'admin_password')
    monkeypatch.setenv('ADMIN_CPF', '12345678900')
    monkeypatch.setenv('ADMIN_NAME', 'Admin User')


def test_create_admin_user_creates_new_user(db_session, mock_env_vars):
    db_session.query.return_value.filter.return_value.first.return_value = None
    with mock.patch(
        'app.services.security.get_password_hash',
        return_value='hashed_password'
    ):
        create_admin_user(db_session)
    assert db_session.add.called
    assert db_session.commit.called
    assert db_session.refresh.called


def test_create_admin_user_already_exists(db_session, mock_env_vars):
    db_session.query.return_value.filter.return_value.first.return_value = (
        models.Customer(
            name='Admin User',
            email='admin@example.com',
            cpf='12345678900',
            hashed_password='hashed_password'
        )
    )
    create_admin_user(db_session)
    assert not db_session.add.called
    assert not db_session.commit.called
    assert not db_session.refresh.called


def test_create_admin_user_missing_env_vars(db_session, monkeypatch):
    monkeypatch.delenv('ADMIN_EMAIL', raising=False)
    create_admin_user(db_session)
    assert not db_session.add.called
    assert not db_session.commit.called
    assert not db_session.refresh.called


def test_create_admin_user_exception_handling(db_session, mock_env_vars):
    db_session.query.side_effect = Exception('Database error')
    create_admin_user(db_session)
    assert not db_session.add.called
    assert not db_session.commit.called
    assert not db_session.refresh.called
