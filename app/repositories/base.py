from typing import Dict, List, Any, Optional


class BaseRepository:
    """Base class for in-memory data repositories."""

    def __init__(self):
        self._storage: Dict[str, Any] = {}

    def create(self, id: str, data: dict) -> dict:
        """Create a new record.

        Args:
            id: Unique identifier for the record
            data: Dictionary containing the record data

        Returns:
            The created record
        """
        self._storage[id] = data
        return data

    def get(self, id: str) -> Optional[dict]:
        """Retrieve a record by ID.

        Args:
            id: Unique identifier

        Returns:
            Record dictionary if found, None otherwise
        """
        return self._storage.get(id)

    def get_all(self) -> List[dict]:
        """Retrieve all records.

        Returns:
            List of all stored records
        """
        return list(self._storage.values())

    def update(self, id: str, data: dict) -> Optional[dict]:
        """Update an existing record.

        Args:
            id: Unique identifier
            data: Dictionary of fields to update

        Returns:
            Updated record if found, None otherwise
        """
        if id in self._storage:
            self._storage[id].update(data)
            return self._storage[id]
        return None

    def delete(self, id: str) -> bool:
        """Delete a record.

        Args:
            id: Unique identifier

        Returns:
            True if deleted, False if not found
        """
        if id in self._storage:
            del self._storage[id]
            return True
        return False

    def exists(self, id: str) -> bool:
        """Check if a record exists.

        Args:
            id: Unique identifier

        Returns:
            True if record exists, False otherwise
        """
        return id in self._storage

    def clear(self):
        """Clear all records from storage."""
        self._storage.clear()
