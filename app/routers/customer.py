from typing import List, Optional, Union
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..database.database import get_db
from ..models import schemas
from ..services import repository, security
from ..tools.logging import logger

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post('/admin', response_model=schemas.Customer)
def create_customer(
    customer: schemas.CustomerCreate,
        db: Session = Depends(get_db),
        current_user: schemas.Customer = Depends(
            security.get_current_user)
) -> schemas.Customer:
    """Cria um novo cliente com as informações fornecidas.

    Args:
        customer (schemas.CustomerCreate): Os dados do cliente para criar.
        db (Session): A sessão do banco de dados.

    Raises:
        HTTPException: Se um cliente com o e-mail fornecido já existir.

    Returns:
        schemas.Customer: O cliente criado.
    """
    logger.info(f'Criando cliente com o e-mail: {customer.email}')
    db_customer = repository.get_user_by_email(db, email=customer.email)
    if db_customer:
        logger.warning(f'Cliente com o e-mail {customer.email} já existe')
        raise HTTPException(status_code=400, detail='E-mail já registrado')
    created_customer = repository.create_user(db=db, user=customer)
    logger.info(f'Cliente criado com ID: {created_customer.id}')
    return created_customer


@router.get(
    '/', response_model=Union[
        schemas.Customer, List[schemas.Customer]]
    )
def get_customers(
    customer_id: Optional[int] = None,
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
):
    """
    Recupera um cliente pelo ID ou uma lista de clientes com paginação.

    - Se `customer_id` for fornecido, retorna um único cliente.
    - Caso contrário, retorna a lista paginada de clientes.

    Args:
        customer_id (Optional[int]): O ID do cliente para recuperar.
        skip (int): O número de registros a serem ignorados.
        limit (int): O número máximo de registros a serem retornados.
        db (Session): A sessão do banco de dados.

    Returns:
        schemas.Customer | List[schemas.Customer]:
        Um cliente específico ou uma lista de clientes.
    """
    if customer_id:
        logger.info(f'Buscando cliente com ID: {customer_id}')
        db_customer = repository.get_customer(db, customer_id=customer_id)

        if db_customer is None:
            logger.warning(f'Cliente com ID {customer_id} não encontrado')
            raise HTTPException(
                status_code=404, detail='Cliente não encontrado'
            )

        # 🔹 Conversão do modelo SQLAlchemy para Pydantic
        return schemas.Customer.model_validate(db_customer)

    logger.info(f'Buscando clientes com skip: {skip}, limit: {limit}')
    db_customers = repository.get_customers(db, skip=skip, limit=limit)

    # 🔹 Conversão do modelo SQLAlchemy para Pydantic (Lista)
    return [
        schemas.Customer.model_validate(customer)
        for customer in db_customers
    ]


@router.post('/identify', response_model=schemas.Customer)
def check_customer(
    cpf: schemas.CPFIdentify,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
) -> schemas.Customer:
    """Identifica um cliente pelo CPF.

    Args:
        cpf (schemas.CPFIdentify): O CPF para identificar o cliente.
        db (Session): A sessão do banco de dados.

    Raises:
        HTTPException: Se o cliente com o CPF fornecido não for encontrado.

    Returns:
        schemas.Customer: O cliente identificado.
    """
    logger.info(f'Identificando cliente com CPF: {cpf.cpf}')
    db_customer = repository.get_customer_by_cpf(db, cpf=cpf.cpf)
    if db_customer is None:
        logger.warning(f'Cliente com CPF {cpf.cpf} não encontrado')
        raise HTTPException(status_code=404, detail='Cliente não encontrado')
    return db_customer


@router.post('/register', response_model=schemas.Customer)
def register_customer(
    customer: schemas.CustomerCreate,
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
) -> schemas.Customer:
    """Registra um novo cliente com as informações fornecidas.

    Args:
        customer (schemas.CustomerCreate): Os dados do cliente para registrar.
        db (Session): A sessão do banco de dados.

    Raises:
        HTTPException: Se um cliente com o e-mail fornecido já existir.

    Returns:
        schemas.Customer: O cliente registrado.
    """
    logger.info(f'Registrando cliente com e-mail: {customer.email}')
    db_customer = repository.get_user_by_email(db, email=customer.email)
    if db_customer:
        logger.warning(f'Cliente com o e-mail {customer.email} já existe')
        raise HTTPException(status_code=400, detail='E-mail já registrado')
    created_customer = repository.create_user(db=db, user=customer)
    logger.info(f'Cliente registrado com ID: {created_customer.id}')
    return created_customer


@router.post('/anonymous', response_model=schemas.Customer)
def create_anonymous_customer(
    db: Session = Depends(get_db),
    current_user: schemas.Customer = Depends(security.get_current_user)
) -> schemas.Customer:
    """Cria um novo cliente anônimo.

    Args:
        db (Session): A sessão do banco de dados.

    Returns:
        schemas.Customer: O cliente anônimo criado.
    """
    logger.info('Criando cliente anônimo')
    anonymous_customer = repository.create_anonymous_customer(db)
    logger.info(f'Cliente anônimo criado com ID: {anonymous_customer.id}')
    return anonymous_customer
