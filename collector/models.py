from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json
import hashlib


class SourceType(str, Enum):
    NEWS_API = "newsapi"
    REDDIT = "reddit"
    RSS = "rss"


@dataclass
class CollectedItem:
    """Normalized content item from any source."""
    source_type: SourceType
    source_name: str          # e.g., "reuters", "r/technology"
    external_id: str          # Original ID from source
    url: str
    title: str
    content: str              # Body text, may be truncated by source
    author: str | None
    published_at: datetime
    collected_at: datetime
    search_phrase: str
    metadata: dict            # Source-specific extras

    @property
    def id(self) -> str:
        """Deterministic ID based on source and external ID."""
        key = f"{self.source_type}:{self.external_id}"
        return hashlib.sha256(key.encode()).hexdigest()[:16]

    def to_json(self) -> str:
        data = asdict(self)
        data["source_type"] = self.source_type.value
        data["published_at"] = self.published_at.isoformat()
        data["collected_at"] = self.collected_at.isoformat()
        data["id"] = self.id
        return json.dumps(data)


@dataclass
class SearchRequest:
    """Parameters for a collection run."""
    phrase: str
    start_date: datetime
    end_date: datetime
    job_id: str               # For tracking/correlation
    sources: list[str] | None = None  # None means all enabled sources
