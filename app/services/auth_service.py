"""Authentication service for login and token management."""

from typing import Optional
from app.repositories.user_repository import UserRepository
from app.utils.jwt_utils import create_access_token
from app.models.user import User


class AuthService:
    """Service for handling authentication."""

    def __init__(self, user_repository: UserRepository):
        self.user_repo = user_repository

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user by email and password.

        For demo purposes, accepts any password.
        In production, verify against hashed password.

        Args:
            email: User email
            password: User password (not validated in demo)

        Returns:
            User object if found, None otherwise
        """
        user_data = self.user_repo.get_by_email(email)
        if user_data:
            return User.from_dict(user_data)
        return None

    def create_token(self, user: User) -> str:
        """Create JWT access token for a user.

        Args:
            user: User object

        Returns:
            JWT token string
        """
        token_data = {
            "user_id": user.id,
            "email": user.email,
            "name": user.name,
            "role": user.role,
        }
        return create_access_token(token_data)

    def get_user_from_token(self, token_data: dict) -> Optional[User]:
        """Get user from decoded token data.

        Args:
            token_data: Decoded JWT payload

        Returns:
            User object if found, None otherwise
        """
        user_id = token_data.get("user_id")
        if user_id:
            return self.user_repo.get_by_id(user_id)
        return None
