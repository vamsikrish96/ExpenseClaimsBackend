"""User model and enums."""

from enum import Enum
from typing import Optional


class UserRole(str, Enum):
    """User roles in the system."""
    EMPLOYEE = "employee"
    MANAGER = "manager"
    FINANCE = "finance"
    ADMIN = "admin"


class User:
    """User model for authentication and authorization."""

    def __init__(
        self,
        id: str,
        email: str,
        name: str,
        role: UserRole,
        manager_id: Optional[str] = None,
    ):
        self.id = id
        self.email = email
        self.name = name
        self.role = role
        self.manager_id = manager_id

    def to_dict(self) -> dict:
        """Convert user to dictionary."""
        return {
            "id": self.id,
            "email": self.email,
            "name": self.name,
            "role": self.role,
            "manager_id": self.manager_id,
        }

    @staticmethod
    def from_dict(data: dict) -> "User":
        """Create user from dictionary."""
        return User(
            id=data["id"],
            email=data["email"],
            name=data["name"],
            role=UserRole(data["role"]),
            manager_id=data.get("manager_id"),
        )
