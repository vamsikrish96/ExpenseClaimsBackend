"""Authentication routes."""

from fastapi import APIRouter, Request
from app.repositories.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.schemas.user import LoginRequest, TokenResponse, UserResponse
from app.schemas.response import SuccessResponse
from app.middleware.error_handler import AuthenticationError

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

user_repo = UserRepository()
auth_service = AuthService(user_repo)


@router.post("/login", response_model=SuccessResponse[TokenResponse])
async def login(request: LoginRequest):
    """User login endpoint.

    Args:
        request: Login request with email and password

    Returns:
        Success response with access token and user info

    Raises:
        AuthenticationError: If credentials are invalid
    """
    user = auth_service.authenticate_user(request.email, request.password)
    if not user:
        raise AuthenticationError("Invalid email or password")

    token = auth_service.create_token(user)
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        role=user.role,
        manager_id=user.manager_id,
    )
    token_response = TokenResponse(access_token=token, user=user_response)

    return SuccessResponse(
        data=token_response,
        message="Login successful",
    )
