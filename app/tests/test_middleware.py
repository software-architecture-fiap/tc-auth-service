from fastapi import FastAPI
from fastapi.testclient import TestClient
from ..middleware.middleware import ExceptionLoggingMiddleware

app = FastAPI()
app.add_middleware(ExceptionLoggingMiddleware)


@app.get("/error")
async def error_route():
    raise ValueError("This is a test error")

client = TestClient(app)


def test_exception_logging_middleware(caplog):
    with caplog.at_level("ERROR"):
        response = client.get("/error")
        assert response.status_code == 500
        assert response.json() == {"detail": "Internal Server Error"}
        assert "Erro Não Tratado: This is a test error" in caplog.text
