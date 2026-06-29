"""Tests for UserRepository."""

import pytest
from app.repositories.user_repository import UserRepository
from app.models.user import UserRole


@pytest.fixture
def user_repo():
    return UserRepository()


def test_get_by_email_existing(user_repo):
    """Test getting user by email."""
    user = user_repo.get_by_email("employee1@company.com")
    assert user is not None
    assert user["email"] == "employee1@company.com"
    assert user["name"] == "Alice Johnson"


def test_get_by_email_nonexistent(user_repo):
    """Test getting non-existent user by email."""
    user = user_repo.get_by_email("nonexistent@company.com")
    assert user is None


def test_get_by_id_existing(user_repo):
    """Test getting user by ID."""
    user = user_repo.get_by_id("user-1")
    assert user is not None
    assert user.id == "user-1"
    assert user.email == "employee1@company.com"


def test_get_by_id_nonexistent(user_repo):
    """Test getting non-existent user by ID."""
    user = user_repo.get_by_id("nonexistent")
    assert user is None


def test_get_by_id_returns_user_object(user_repo):
    """Test that get_by_id returns User object."""
    from app.models.user import User
    user = user_repo.get_by_id("user-3")
    assert isinstance(user, User)
    assert user.role == UserRole.MANAGER


def test_get_team_members(user_repo):
    """Test getting team members managed by a manager."""
    team = user_repo.get_team_members("user-3")
    assert len(team) == 2
    emails = [m["email"] for m in team]
    assert "employee1@company.com" in emails
    assert "employee2@company.com" in emails


def test_get_team_members_no_team(user_repo):
    """Test getting team members for manager with no team."""
    team = user_repo.get_team_members("user-4")
    assert len(team) == 0


def test_get_team_members_nonexistent_manager(user_repo):
    """Test getting team members for non-existent manager."""
    team = user_repo.get_team_members("nonexistent")
    assert len(team) == 0


def test_test_users_created(user_repo):
    """Test that test users are created on initialization."""
    all_users = user_repo.get_all()
    assert len(all_users) == 5

    emails = [u["email"] for u in all_users]
    assert "employee1@company.com" in emails
    assert "employee2@company.com" in emails
    assert "manager1@company.com" in emails
    assert "finance1@company.com" in emails
    assert "admin1@company.com" in emails


def test_test_users_have_correct_roles(user_repo):
    """Test that test users have correct roles assigned."""
    user_map = {u["email"]: u for u in user_repo.get_all()}

    assert user_map["employee1@company.com"]["role"] == UserRole.EMPLOYEE
    assert user_map["manager1@company.com"]["role"] == UserRole.MANAGER
    assert user_map["finance1@company.com"]["role"] == UserRole.FINANCE
    assert user_map["admin1@company.com"]["role"] == UserRole.ADMIN
