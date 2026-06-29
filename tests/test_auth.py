"""Tests for authentication system."""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.models.user import UserRole


@pytest.fixture
def client():
    return TestClient(app)


def test_login_success(client):
    """Test successful login."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee1@company.com", "password": "any_password"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "data" in data
    assert "access_token" in data["data"]
    assert data["data"]["token_type"] == "bearer"
    assert data["data"]["user"]["email"] == "employee1@company.com"
    assert data["data"]["user"]["role"] == UserRole.EMPLOYEE


def test_login_invalid_email(client):
    """Test login with non-existent email."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@company.com", "password": "password"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["success"] is False
    assert data["error"] == "authentication_error"


def test_login_returns_user_info(client):
    """Test that login returns complete user information."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "manager1@company.com", "password": "password"},
    )
    assert response.status_code == 200
    user_data = response.json()["data"]["user"]
    assert user_data["id"] == "user-3"
    assert user_data["name"] == "Charlie Brown"
    assert user_data["role"] == UserRole.MANAGER
    assert user_data["manager_id"] is None


def test_login_with_manager_info(client):
    """Test that employee login returns manager ID."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee1@company.com", "password": "password"},
    )
    assert response.status_code == 200
    user_data = response.json()["data"]["user"]
    assert user_data["manager_id"] == "user-3"


def test_login_different_roles(client):
    """Test login for different user roles."""
    test_cases = [
        ("employee1@company.com", UserRole.EMPLOYEE),
        ("manager1@company.com", UserRole.MANAGER),
        ("finance1@company.com", UserRole.FINANCE),
        ("admin1@company.com", UserRole.ADMIN),
    ]

    for email, expected_role in test_cases:
        response = client.post(
            "/api/v1/auth/login",
            json={"email": email, "password": "password"},
        )
        assert response.status_code == 200
        user_data = response.json()["data"]["user"]
        assert user_data["role"] == expected_role


def test_token_format(client):
    """Test that returned token is a valid JWT format."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee1@company.com", "password": "password"},
    )
    assert response.status_code == 200
    token = response.json()["data"]["access_token"]
    parts = token.split(".")
    assert len(parts) == 3  # JWT has 3 parts separated by dots


def test_invalid_email_format(client):
    """Test login with invalid email format."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "not-an-email", "password": "password"},
    )
    assert response.status_code == 422  # Validation error


def test_missing_email_field(client):
    """Test login with missing email."""
    response = client.post(
        "/api/v1/auth/login",
        json={"password": "password"},
    )
    assert response.status_code == 422  # Validation error


def test_missing_password_field(client):
    """Test login with missing password."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "employee1@company.com"},
    )
    assert response.status_code == 422  # Validation error
