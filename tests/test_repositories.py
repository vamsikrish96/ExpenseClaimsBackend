import pytest
from app.repositories.base import BaseRepository


@pytest.fixture
def repo():
    return BaseRepository()


def test_create(repo):
    data = {"id": "1", "name": "Test"}
    result = repo.create("1", data)
    assert result == data


def test_get(repo):
    data = {"id": "1", "name": "Test"}
    repo.create("1", data)
    result = repo.get("1")
    assert result == data


def test_get_nonexistent(repo):
    result = repo.get("nonexistent")
    assert result is None


def test_get_all(repo):
    repo.create("1", {"id": "1"})
    repo.create("2", {"id": "2"})
    result = repo.get_all()
    assert len(result) == 2


def test_update(repo):
    repo.create("1", {"id": "1", "name": "Original"})
    repo.update("1", {"name": "Updated"})
    result = repo.get("1")
    assert result["name"] == "Updated"


def test_delete(repo):
    repo.create("1", {"id": "1"})
    assert repo.delete("1")
    assert repo.get("1") is None


def test_exists(repo):
    repo.create("1", {"id": "1"})
    assert repo.exists("1")
    assert not repo.exists("nonexistent")


def test_clear(repo):
    repo.create("1", {"id": "1"})
    repo.clear()
    assert len(repo.get_all()) == 0
