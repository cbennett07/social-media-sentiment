from abc import ABC, abstractmethod
from typing import Iterator
from collector.models import CollectedItem, SearchRequest


class SourceAdapter(ABC):
    """Base class for all content sources."""

    @property
    @abstractmethod
    def source_type(self) -> str:
        """Identifier for this source type."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @abstractmethod
    def search(self, request: SearchRequest) -> Iterator[CollectedItem]:
        """
        Yield collected items matching the search request.

        Implementations should handle pagination internally and yield
        items as they're retrieved to support streaming to the queue.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        """Verify the source is reachable and credentials are valid."""
        pass
