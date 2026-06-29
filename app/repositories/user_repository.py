"""User repository for in-memory user storage."""

from typing import Optional, List
from app.repositories.base import BaseRepository
from app.models.user import User, UserRole


class UserRepository(BaseRepository):
    """Repository for managing users."""

    def __init__(self):
        super().__init__()
        self._setup_test_users()

    def _setup_test_users(self):
        """Initialize test users for demo purposes."""
        test_users = [
            User(
                id="user-1",
                email="employee1@company.com",
                name="Alice Johnson",
                role=UserRole.EMPLOYEE,
                manager_id="user-3",
            ),
            User(
                id="user-2",
                email="employee2@company.com",
                name="Bob Smith",
                role=UserRole.EMPLOYEE,
                manager_id="user-3",
            ),
            User(
                id="user-3",
                email="manager1@company.com",
                name="Charlie Brown",
                role=UserRole.MANAGER,
            ),
            User(
                id="user-4",
                email="finance1@company.com",
                name="Diana Prince",
                role=UserRole.FINANCE,
            ),
            User(
                id="user-5",
                email="admin1@company.com",
                name="Eve Wilson",
                role=UserRole.ADMIN,
            ),
        ]
        for user in test_users:
            self.create(user.id, user.to_dict())

    def get_by_email(self, email: str) -> Optional[dict]:
        """Get user by email.

        Args:
            email: User email

        Returns:
            User dictionary if found, None otherwise
        """
        for user_data in self.get_all():
            if user_data["email"] == email:
                return user_data
        return None

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get user by ID and return as User object.

        Args:
            user_id: User ID

        Returns:
            User object if found, None otherwise
        """
        user_data = self.get(user_id)
        if user_data:
            return User.from_dict(user_data)
        return None

    def get_team_members(self, manager_id: str) -> List[dict]:
        """Get all employees managed by a manager.

        Args:
            manager_id: Manager's user ID

        Returns:
            List of employee dictionaries
        """
        return [
            user for user in self.get_all()
            if user.get("manager_id") == manager_id
        ]
