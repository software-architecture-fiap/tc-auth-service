from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import jwt, JWTError
from os import environ as env
from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext

from ..database.database import get_db
from ..models import schemas
from ..services import repository
from ..tools.logging import logger

# Configuração do JWT
SECRET_KEY = env.get("SECRET_KEY", "")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_by_email(db: Session, email: str):
    """Movendo a importação para dentro da função para evitar erro de
    importação circular"""
    from ..services.repository import get_user_by_email
    return get_user_by_email(db, email)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(
        minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(db: Session = Depends(get_db),
                     token: str = Depends(oauth2_scheme)) -> schemas.Customer:
    """Verifica e retorna o usuário autenticado a partir do token JWT."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou expiradas",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")

        if user_id is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    # Buscar usuário no banco de dados
    user = repository.get_customer(db, customer_id=user_id)
    if user is None:
        raise credentials_exception

    return user


def get_password_hash(password: str) -> str:
    """Gera um hash para a senha fornecida.

    Args:
        password (str): Senha a ser criptografada.

    Returns:
        str: Senha criptografada.
    """
    logger.debug('Hashing password')
    return pwd_context.hash(password)
