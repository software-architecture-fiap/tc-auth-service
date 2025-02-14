import pytest
from fastapi import status
from fastapi.testclient import TestClient
from types import SimpleNamespace

from app.main import app

client = TestClient(app)

@pytest.fixture
def mock_user():
    """Usuário mockado para os testes"""
    return SimpleNamespace(
        id=1,
        email="admin@fiap.com.br",
        hashed_password="$2b$12$wU3o3gQxELZfiMjri7FxNODcDbUGbeLy8wPOpvpb1JHxH33jWrxvq"
    )

def test_auth_success(mocker, mock_user):
    """Teste de autenticação com credenciais corretas"""
    mocker.patch("app.services.repository.get_user_by_email", return_value=mock_user)
    mocker.patch("app.services.security.verify_password", return_value=True)
    mocker.patch("app.services.security.create_access_token", return_value="mock_access_token")

    form_data = {"username": "admin@fiap.com.br", "password": "valid_password"}
    response = client.post("/token", data=form_data)

    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_auth_invalid_credentials(mocker):
    """Teste de autenticação com credenciais inválidas"""
    mocker.patch("app.services.repository.get_user_by_email", return_value=None)

    form_data = {"username": "invalid@example.com", "password": "wrong_password"}
    response = client.post("/token", data=form_data)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "msg" in response.json() 
