"""Tests for authorization and role-based access control."""

import pytest
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from app.middleware.auth import require_role, _extract_token_payload
from app.middleware.error_handler import setup_error_handlers, AuthorizationError, AuthenticationError
from app.utils.jwt_utils import create_access_token
from app.models.user import UserRole


def test_extract_token_payload_valid():
    """Test extracting token payload from valid authorization header."""
    token_data = {"user_id": "123", "role": UserRole.EMPLOYEE}
    token = create_access_token(token_data)

    app = FastAPI()

    @app.get("/test")
    async def test_endpoint(request: Request):
        payload = _extract_token_payload(request)
        return payload

    client = TestClient(app)
    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["user_id"] == "123"


def test_extract_token_payload_missing_header():
    """Test that missing authorization header raises error."""
    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    async def test_endpoint(request: Request):
        return _extract_token_payload(request)

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"


def test_extract_token_payload_invalid_format():
    """Test that invalid header format raises error."""
    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    async def test_endpoint(request: Request):
        return _extract_token_payload(request)

    client = TestClient(app)
    response = client.get("/test", headers={"Authorization": "InvalidFormat"})
    assert response.status_code == 401


def test_require_role_allows_correct_role():
    """Test that require_role decorator allows users with correct role."""
    token_data = {"user_id": "123", "role": UserRole.MANAGER.value}
    token = create_access_token(token_data)

    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    @require_role(UserRole.MANAGER)
    async def test_endpoint(request: Request, current_user: dict = None):
        return {"message": "success"}

    client = TestClient(app)
    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["message"] == "success"


def test_require_role_denies_wrong_role():
    """Test that require_role decorator denies users without required role."""
    token_data = {"user_id": "123", "role": UserRole.EMPLOYEE.value}
    token = create_access_token(token_data)

    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    @require_role(UserRole.MANAGER)
    async def test_endpoint(request: Request, current_user: dict = None):
        return {"message": "success"}

    client = TestClient(app)
    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403
    assert response.json()["error"] == "authorization_error"


def test_require_role_multiple_roles():
    """Test that require_role allows any of multiple specified roles."""
    test_cases = [
        (UserRole.MANAGER.value, True),
        (UserRole.FINANCE.value, True),
        (UserRole.EMPLOYEE.value, False),
    ]

    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    @require_role(UserRole.MANAGER, UserRole.FINANCE)
    async def test_endpoint(request: Request, current_user: dict = None):
        return {"message": "success"}

    client = TestClient(app)

    for role, should_succeed in test_cases:
        token_data = {"user_id": "123", "role": role}
        token = create_access_token(token_data)
        response = client.get("/test", headers={"Authorization": f"Bearer {token}"})

        if should_succeed:
            assert response.status_code == 200
        else:
            assert response.status_code == 403


def test_require_role_missing_token():
    """Test that require_role denies request without token."""
    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    @require_role(UserRole.MANAGER)
    async def test_endpoint(request: Request, current_user: dict = None):
        return {"message": "success"}

    client = TestClient(app)
    response = client.get("/test")
    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"


def test_require_role_expired_token():
    """Test that require_role denies request with expired token."""
    from datetime import timedelta

    token_data = {"user_id": "123", "role": UserRole.MANAGER.value}
    token = create_access_token(token_data, expires_delta=timedelta(seconds=-1))

    app = FastAPI()
    setup_error_handlers(app)

    @app.get("/test")
    @require_role(UserRole.MANAGER)
    async def test_endpoint(request: Request, current_user: dict = None):
        return {"message": "success"}

    client = TestClient(app)
    response = client.get("/test", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["error"] == "authentication_error"
