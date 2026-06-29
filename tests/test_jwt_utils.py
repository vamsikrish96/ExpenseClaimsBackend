import pytest
from datetime import timedelta
from app.utils.jwt_utils import create_access_token, decode_access_token


def test_create_access_token():
    data = {"user_id": "123", "role": "employee"}
    token = create_access_token(data)
    assert token is not None
    assert isinstance(token, str)


def test_decode_access_token():
    data = {"user_id": "123", "role": "employee"}
    token = create_access_token(data)
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["user_id"] == "123"
    assert decoded["role"] == "employee"


def test_decode_invalid_token():
    result = decode_access_token("invalid_token")
    assert result is None


def test_token_with_custom_expiry():
    data = {"user_id": "123"}
    token = create_access_token(data, expires_delta=timedelta(hours=1))
    decoded = decode_access_token(token)
    assert decoded is not None
    assert decoded["user_id"] == "123"
