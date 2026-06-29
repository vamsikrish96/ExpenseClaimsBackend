"""Authentication middleware and decorators."""

from functools import wraps
from typing import Callable, List, Optional
from fastapi import Depends, Request
from app.utils.jwt_utils import decode_access_token
from app.middleware.error_handler import AuthenticationError, AuthorizationError
from app.models.user import UserRole, User


async def get_current_user(request: Request) -> dict:
    """Get current user from authorization header.

    Args:
        request: FastAPI request object

    Returns:
        Decoded token data (user info)

    Raises:
        AuthenticationError: If token is missing or invalid
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header:
        raise AuthenticationError("Missing authorization header")

    parts = auth_header.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise AuthenticationError("Invalid authorization header format")

    token = parts[1]
    payload = decode_access_token(token)
    if not payload:
        raise AuthenticationError("Invalid or expired token")

    return payload


def require_role(*allowed_roles: UserRole) -> Callable:
    """Decorator to require specific roles for an endpoint.

    Args:
        *allowed_roles: UserRole values that are allowed

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, request: Request = None, **kwargs):
            auth_header = request.headers.get("Authorization")
            if not auth_header:
                raise AuthenticationError("Missing authorization header")

            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != "bearer":
                raise AuthenticationError("Invalid authorization header format")

            token = parts[1]
            payload = decode_access_token(token)
            if not payload:
                raise AuthenticationError("Invalid or expired token")

            user_role = payload.get("role")
            if user_role not in [role.value for role in allowed_roles]:
                raise AuthorizationError(
                    f"This action requires one of these roles: {', '.join([r.value for r in allowed_roles])}"
                )

            return await func(*args, **kwargs, current_user=payload)

        return wrapper
    return decorator
