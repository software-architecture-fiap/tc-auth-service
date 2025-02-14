# Auth Service - Sistema de Autenticação

Este repositório contém o serviço de autenticação (`auth-service`) de um sistema de lanchonete, responsável por gerenciar a autenticação de usuários, criação de tokens de acesso, e integração com outros serviços do sistema.

## Visão Geral

O **Auth Service** é o componente responsável pela autenticação de usuários, incluindo a geração de tokens JWT para autenticação em outros serviços. Ele também oferece endpoints para o gerenciamento de usuários.

### Funcionalidades

- **Autenticação de usuários**: Geração de tokens JWT para autenticação.
- **Cadastro de usuários**: Permite que novos usuários se cadastrem no sistema.
- **Validação de tokens**: Valida se os tokens enviados em requisições são válidos.
- **Integração com outros serviços**: O **Auth Service** é consumido por outros serviços para validar a autenticidade de requisições.

## Tecnologias

- **FastAPI**: Framework para construir APIs rápidas e eficientes.
- **JWT (JSON Web Tokens)**: Utilizado para geração e validação de tokens de autenticação.
- **SQLAlchemy**: ORM para interação com o banco de dados.
- **PostgreSQL**: Banco de dados relacional utilizado para armazenar informações de usuários.
- **Docker**: Para containerizar a aplicação.
- **Pydantic**: Para validação de dados e esquemas.

## Pré-requisitos

- **Python 3.10+**
- **Docker & Docker Compose** (para containers)
- **PostgreSQL** (para armazenamento de usuários)

## Instalação

### 1. Clonar o repositório

Clone o repositório para sua máquina local:

```bash
git clone <<url>>
cd auth-service
```

### 2. Criar um ambiente virtual

Crie e ative um ambiente virtual:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Para macOS/Linux
.venv\Scripts\activate     # Para Windows
```

### 3. Instalar as dependências

Instale as dependências do projeto:

```bash
pip install poetry
poetry install
```

### 4. Configuração do banco de dados

O **Auth Service** utiliza o PostgreSQL como banco de dados. Você pode usar o Docker para rodar uma instância do PostgreSQL localmente.

#### Usando Docker (para desenvolvimento)

Execute o seguinte comando para iniciar o PostgreSQL:

```bash
docker-compose up -d
```

#### Variáveis de ambiente

Crie um arquivo `.env` com as seguintes variáveis:

```bash
DATABASE_URL= "<<suaconexão>>"
SECRET_KEY= "<<chave_secreta>>"

# dados do seu user admin
ADMIN_NAME=""
ADMIN_EMAIL=""
ADMIN_CPF=""
ADMIN_PASSWORD=""
```

- `DATABASE_URL`: URL de conexão com o banco de dados PostgreSQL.
- `SECRET_KEY`: Chave secreta para assinatura dos tokens JWT.

### 5. Inicializar a aplicação

Execute o comando abaixo para iniciar a aplicação:

```bash
docker-compose up --build -d
```

Isso criará o banco de dados e o serviço.

### 6. Executar o servidor de desenvolvimento

O servidor estará disponível em `http://127.0.0.1:8000`.

## Endpoints API

A API do **Auth Service** possui os seguintes endpoints:

### Endpoints

- `POST /token`: Solicita um bearer token.
- `GET /auth`: Valida a autorização do bearer token.
- `POST /customers/admin`: Cria o usuário administrador da aplicação
- `GET /customer/`: Recupera a lista de usuários cadastrados.
- `POST /customer/identify`: Identifica um usuário pelo CPF.
- `POST /customer/register`: Criar o usuário identificado.
- `POST /customer/anonymous`: Criar o usuário anônimo.

## Testes

Para executar os testes automatizados com `pytest`, use o seguinte comando:

```bash
pytest
```

Isso executará todos os testes definidos no repositório.

### Testes unitários

A suíte de testes também inclui testes unitários para verificar o comportamento das funções e métodos principais.

## Deploy

Para produção, recomenda-se o uso de Docker e Docker Compose para orquestrar os containers de forma eficiente. O arquivo `docker-compose.yml` pode ser configurado para criar e gerenciar os containers em um ambiente de produção.

1. **Construir os containers**:

```bash
docker-compose up -d --build
```

2. **Acessar o serviço em produção**

Após o deploy, a API estará acessível no endereço especificado no arquivo `docker-compose.yml`.

## Contribuindo

1. Faça o fork deste repositório.
2. Crie uma nova branch (`git checkout -b feature/nova-feature`).
3. Faça suas alterações e commit (`git commit -am 'Adicionando nova feature'`).
4. Faça o push para a branch (`git push origin feature/nova-feature`).
5. Abra um pull request.

## Licença

Este projeto está licenciado sob a MIT License - veja o arquivo [LICENSE](LICENSE) para mais detalhes.

---

Se você encontrar problemas ou tiver dúvidas, sinta-se à vontade para abrir um *issue* ou fazer uma contribuição!
