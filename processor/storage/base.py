from abc import ABC, abstractmethod


class ObjectStorage(ABC):
    """Abstract interface for object storage (S3-compatible)."""

    @abstractmethod
    def put(self, key: str, data: str | bytes) -> str:
        """
        Store data at the given key.

        Args:
            key: The object key/path
            data: The data to store (string or bytes)

        Returns:
            The full path/URI of the stored object
        """
        pass

    @abstractmethod
    def get(self, key: str) -> bytes:
        """
        Retrieve data from the given key.

        Args:
            key: The object key/path

        Returns:
            The stored data as bytes
        """
        pass

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if an object exists at the given key."""
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify the storage service is accessible."""
        pass
