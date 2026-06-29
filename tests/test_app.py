import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.main import app
from app.middleware.error_handler import (
    ValidationError,
    AuthenticationError,
    AuthorizationError,
    BusinessLogicError,
)


@pytest.fixture
def client():
    return TestClient(app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["status"] == "healthy"


def test_health_endpoint_uses_response_wrapper(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data
    assert "data" in data
    assert "timestamp" in data


def test_error_handling_validation(client):
    response = client.post("/nonexistent")
    assert response.status_code in [404, 405]


def test_validation_error_handler():
    test_app = FastAPI()
    from app.middleware.error_handler import setup_error_handlers
    setup_error_handlers(test_app)

    @test_app.get("/test-validation")
    def test_endpoint():
        raise ValidationError("Test validation error", {"field": "test"})

    client = TestClient(test_app)
    response = client.get("/test-validation")
    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "validation_error"
    assert "Test validation error" in data["message"]
    assert data["details"] == {"field": "test"}


def test_authentication_error_handler():
    test_app = FastAPI()
    from app.middleware.error_handler import setup_error_handlers
    setup_error_handlers(test_app)

    @test_app.get("/test-auth")
    def test_endpoint():
        raise AuthenticationError("Invalid credentials")

    client = TestClient(test_app)
    response = client.get("/test-auth")
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "authentication_error"


def test_authorization_error_handler():
    test_app = FastAPI()
    from app.middleware.error_handler import setup_error_handlers
    setup_error_handlers(test_app)

    @test_app.get("/test-authz")
    def test_endpoint():
        raise AuthorizationError("Admin access required")

    client = TestClient(test_app)
    response = client.get("/test-authz")
    assert response.status_code == 403
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "authorization_error"


def test_business_logic_error_handler():
    test_app = FastAPI()
    from app.middleware.error_handler import setup_error_handlers
    setup_error_handlers(test_app)

    @test_app.get("/test-business")
    def test_endpoint():
        raise BusinessLogicError("Budget exceeded")

    client = TestClient(test_app)
    response = client.get("/test-business")
    assert response.status_code == 422
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "business_logic_error"
