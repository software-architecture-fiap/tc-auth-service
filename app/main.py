import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from starlette.status import (
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_500_INTERNAL_SERVER_ERROR,
)
from contextlib import asynccontextmanager
from fastapi.responses import HTMLResponse

from .middleware.middleware import ExceptionLoggingMiddleware
from .routers import auth, customer
from .tools.logging import logger
from .services.repository import create_admin_user
from .database.database import Base, SessionLocal, engine

Base.metadata.create_all(bind=engine)


def init_admin_user() -> None:
    """Inicializa o usuário admin e configura o banco de dados.

    Cria um usuário administrador e inicializa o banco de dados com dados
    padrão.

    Returns:
        None
    """
    db = SessionLocal()
    try:
        create_admin_user(db)
    finally:
        db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Executa tarefas antes de iniciar a API"""
    init_admin_user()
    yield
    print("Aplicação encerrando...")

app = FastAPI(lifespan=lifespan)
logger.info('Application startup')

# Configuração do CORS
origins = [
    'http://localhost',
    'http://localhost:8000',
    'http://localhost:8001',
    'http://localhost:8002',
]

#  Define o esquema de autenticação OAuth2 com fluxo de senha
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", scheme_name="JWT")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

# Incluindo os roteadores
app.add_middleware(ExceptionLoggingMiddleware)
app.include_router(auth.router, tags=['authentication'])
app.include_router(customer.router, prefix='/customers', tags=['customers'])


STATUS_CODE = "status code"


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    logger.error(f"Validation error: {exc}")
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            STATUS_CODE: 422,
            "msg": (
                f"Validation error in request body or parameters: "
                f"{exc.errors()}"
            )
        },
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    logger.error(f"HTTP error: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={
            STATUS_CODE: exc.status_code,
            "msg": exc.detail,
        },
    )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unexpected server error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            STATUS_CODE: 500,
            "msg": """
                    An unexpected error occurred.
                    Please try again later or contact your Support Team.
                   """
        },
    )


@app.get('/health', tags=['health'])
def health_check() -> dict:
    """Retorna o status operacional da aplicação.

    Returns:
        dict: Um dicionário com o status da aplicação.
    """
    logger.debug('Status endpoint accessed')
    return {'status': 'Operational'}


@app.get('/redoc', include_in_schema=False, tags=['documentation'])
async def redoc() -> HTMLResponse:
    """Retorna o HTML para a documentação do ReDoc.

    Returns:
        HTMLResponse: O HTML da documentação do ReDoc.
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + ' - ReDoc',
        redoc_js_url=(
            'https://cdn.jsdelivr.net/npm/redoc/bundles/redoc.standalone.js'
        ),
    )


@app.get('/docs', tags=['documentation'])
def get_docs():
    return app.openapi()


def run_server():
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)


if __name__ == '__main__':
    run_server()
