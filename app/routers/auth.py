from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from starlette.status import HTTP_401_UNAUTHORIZED

from ..database.database import get_db
from ..models import schemas
from ..services import security
from ..tools.logging import logger

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post("/token", response_model=schemas.Token)
def generate_token(
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Autentica um usuário e retorna um token JWT."""
    user = security.get_user_by_email(db, form_data.username)
    if not user or not security.verify_password(
        form_data.password, user.hashed_password
    ):
        logger.error("Credenciais inválidas")
        raise HTTPException(status_code=400, detail="Credenciais inválidas")

    access_token = security.create_access_token(data={"sub": str(user.id)})

    return schemas.Token(
        access_token=access_token,
        token_type="bearer",
        customer_id=str(user.id)
    )


@router.get("/auth", response_model=schemas.Customer)
def validate_token(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
):
    """Valida um token JWT e retorna os detalhes do usuário autenticado."""
    try:
        user = security.get_current_user(db, token)
        return user
    except HTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception:
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
