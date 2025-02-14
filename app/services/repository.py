import os
from typing import List, Optional
from dotenv import load_dotenv
from sqlalchemy.orm import Session

from ..models import models, schemas
from ..tools.logging import logger
from . import security

load_dotenv()

# ======= CUSTOMER ADMIN ======= #

def create_admin_user(db: Session) -> None:
    """Cria um usuário administrador se ele ainda não existir.

    Os detalhes do administrador (nome, email, senha, CPF) devem ser fornecidos
    através de variáveis de ambiente: `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `ADMIN_CPF`, `ADMIN_NAME`.

    Args:
        db (Session): Sessão do banco de dados.

    Raises:
        Exception: Se houver algum erro ao criar o usuário administrador.
    """
    try:
        admin_email = os.getenv('ADMIN_EMAIL')
        admin_password = os.getenv('ADMIN_PASSWORD')
        admin_cpf = os.getenv('ADMIN_CPF')
        admin_name = os.getenv('ADMIN_NAME')

        if not all([admin_email, admin_password, admin_cpf, admin_name]):
            logger.error('Admin user details are not set in environment variables.')
            return

        logger.debug(f'Admin email: {admin_email}, Admin name: {admin_name}')

        user = db.query(models.Customer).filter(models.Customer.email == admin_email).first()
        if not user:
            hashed_password = security.get_password_hash(admin_password)
            admin_user = models.Customer(
                name=admin_name, email=admin_email, cpf=admin_cpf, hashed_password=hashed_password
            )
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            logger.debug(f'Admin user created with email: {admin_email}')
        else:
            logger.debug(f'Admin user already exists with email: {admin_email}')
    except Exception as e:
        logger.error(f'Error creating admin user: {e}')

def create_user(db: Session, user: schemas.CustomerCreate) -> models.Customer:
    """Cria um novo usuário.

    Args:
        db (Session): Sessão do banco de dados.
        user (schemas.CustomerCreate): Os dados do usuário a ser criado.

    Returns:
        models.Customer: O usuário criado.
    """
    logger.debug(f'Creating user with email: {user.email}')
    hashed_password = security.get_password_hash(user.password)
    db_user = models.Customer(name=user.name, email=user.email, cpf=user.cpf, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    logger.info(f'User created with ID: {db_user.id}')
    return db_user

def create_customer(db: Session, customer: schemas.CustomerCreate) -> models.Customer:
    """Cria um novo cliente.

    Args:
        db (Session): Sessão do banco de dados.
        customer (schemas.CustomerCreate): Dados do cliente a ser criado.

    Returns:
        models.Customer: O cliente criado.
    """
    logger.debug(f'Creating customer with email: {customer.email}')
    db_customer = models.Customer(name=customer.name, email=customer.email, cpf=customer.cpf)
    db.add(db_customer)
    db.commit()
    db.refresh(db_customer)
    logger.info(f'Customer created with ID: {db_customer.id}')
    return db_customer

def create_anonymous_customer(db: Session) -> models.Customer:
    """Cria um cliente anônimo.

    Args:
        db (Session): Sessão do banco de dados.

    Returns:
        models.Customer: O cliente anônimo criado.
    """
    logger.debug('Creating anonymous customer')
    anonymous_customer = models.Customer(name='Anonymous', email=None, cpf=None, hashed_password=None)
    db.add(anonymous_customer)
    db.commit()
    db.refresh(anonymous_customer)
    logger.info(f'Anonymous customer created with ID: {anonymous_customer.id}')
    return anonymous_customer

def get_user_by_email(db: Session, email: str) -> models.Customer:
    """Obtém um usuário pelo endereço de e-mail.

    Args:
        db (Session): Sessão do banco de dados.
        email (str): O endereço de e-mail do usuário.

    Returns:
        models.Customer: O usuário encontrado, ou None se nenhum usuário for encontrado.
    """
    logger.info(f'Fetching user with email: {email}')
    return db.query(models.Customer).filter(models.Customer.email == email).first()

def get_customer_by_cpf(db: Session, cpf: str) -> models.Customer:
    """Obtém um cliente pelo CPF.

    Args:
        db (Session): Sessão do banco de dados.
        cpf (str): O CPF do cliente.

    Returns:
        models.Customer: O cliente encontrado, ou None se nenhum cliente for encontrado.
    """
    logger.debug(f'Fetching customer with CPF: {cpf}')
    return db.query(models.Customer).filter(models.Customer.cpf == cpf).first()

def get_customers_count(db: Session) -> int:
    """Obtém a contagem total de clientes.

    Args:
        db (Session): Sessão do banco de dados.

    Returns:
        int: O número total de clientes.
    """
    logger.info('Fetching total count of customers')
    return db.query(models.Customer).count()

def get_customer(db: Session, customer_id: int) -> Optional[models.Customer]:
    """Obtém um cliente pelo ID.

    Args:
        db (Session): Sessão do banco de dados.
        customer_id (int): ID do cliente.

    Returns:
        Optional[models.Customer]: O cliente encontrado ou None se nenhum cliente for encontrado.
    """
    logger.debug(f'Fetching customer with ID: {customer_id}')
    try:
        return db.query(models.Customer).filter(models.Customer.id == customer_id).first()
    except Exception as e:
        logger.error(f'Error fetching customer: {e}')
        return None

def get_customers(db: Session, skip: int = 0, limit: int = 10) -> List[models.Customer]:
    """Obtém uma lista de clientes com paginação.

    Args:
        db (Session): Sessão do banco de dados.
        skip (int, optional): Número de registros a pular. Defaults to 0.
        limit (int, optional): Número máximo de registros a retornar. Defaults to 10.

    Returns:
        List[models.Customer]: Lista de clientes.
    """
    logger.debug(f'Fetching customers with skip: {skip}, limit: {limit}')
    return db.query(models.Customer).offset(skip).limit(limit).all()
