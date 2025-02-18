from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..database.database import Base


class Customer(Base):
    """
    Representa um Cliente na Base de Dados.

    Attributes:
        id (int): Identificador único do cliente.
        name (str): Nome do cliente.
        email (str): Email do cliente.
        cpf (str): CPF do cliente.
        hashed_password (str): Senha do cliente criptografada.
        orders (relationship): Relacionamento com pedidos associados ao 
        cliente.
    """

    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    cpf = Column(String, unique=True, index=True)
    hashed_password = Column(String)


class Token(Base):
    """
    Representa um Token de Autenticação.

    Attributes:
        id (int): Identificador único do token.
        token (str): Valor do token.
        is_used (bool): Indica se o token foi utilizado.
        user_id (int): Identificador do cliente associado ao token.
        user (relationship): Relacionamento com o cliente associado ao token.
    """

    __tablename__ = 'tokens'

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True)
    is_used = Column(Boolean, default=False)
    user_id = Column(Integer, ForeignKey('customers.id'))

    user = relationship('Customer')
