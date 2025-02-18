from typing import Optional
from pydantic import BaseModel, ConfigDict


class CustomerBase(BaseModel):
    """
    Modelo Base para Dados de Clientes.

    Attributes:
        name (Optional[str]): Nome do cliente.
        email (Optional[str]): Email do cliente.
        cpf (Optional[str]): CPF do cliente.
    """

    name: Optional[str] = None
    email: Optional[str] = None
    cpf: Optional[str] = None


class CustomerCreate(CustomerBase):
    """
    Modelo para Criação de um Novo Cliente.

    Attributes:
        password (Optional[str]): Senha do cliente.
    """

    password: Optional[str] = None


class Customer(CustomerBase):
    """
    Modelo para Dados Completos do Cliente.

    Attributes:
        id (int): Identificador único do cliente.
    """

    id: int

    class Tracking:
        """
        Configurações específicas para o modelo Pydantic `Tracking`.
        """

        model_config = ConfigDict(from_attributes=True)


class CPFIdentify(BaseModel):
    """
    Modelo para Identificação por CPF.

    Attributes:
        cpf (str): CPF do cliente.
    """

    cpf: str


class Token(BaseModel):
    """
    Modelo para um Token de Autenticação.

    Attributes:
        access_token (str): Token de acesso.
        customer_id (int): Identificador do cliente associado ao token.
    """

    access_token: str
    customer_id: int


class TokenData(BaseModel):
    """
    Modelo para Dados do Token.

    Attributes:
        username (Optional[str]): Nome de usuário associado ao token.
    """

    username: Optional[str] = None


class TokenRequest(BaseModel):
    username: str
    password: str
