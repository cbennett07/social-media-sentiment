from dataclasses import dataclass, asdict
from datetime import datetime
from enum import Enum
import json


class Sentiment(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


@dataclass
class Theme:
    """A theme extracted from content."""
    name: str
    confidence: float  # 0.0 to 1.0
    keywords: list[str]


@dataclass
class Analysis:
    """Result of LLM analysis on a piece of content."""
    themes: list[Theme]
    sentiment: Sentiment
    sentiment_score: float  # -1.0 to 1.0
    summary: str
    key_points: list[str]
    entities: list[str]  # People, organizations, locations mentioned

    def to_dict(self) -> dict:
        return {
            "themes": [asdict(t) for t in self.themes],
            "sentiment": self.sentiment.value,
            "sentiment_score": self.sentiment_score,
            "summary": self.summary,
            "key_points": self.key_points,
            "entities": self.entities,
        }


@dataclass
class ProcessedItem:
    """A fully processed content item with analysis."""
    id: str
    source_type: str
    source_name: str
    url: str
    title: str
    content: str
    author: str | None
    published_at: datetime
    collected_at: datetime
    processed_at: datetime
    search_phrase: str
    analysis: Analysis
    raw_storage_path: str

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "source_type": self.source_type,
            "source_name": self.source_name,
            "url": self.url,
            "title": self.title,
            "content": self.content,
            "author": self.author,
            "published_at": self.published_at.isoformat(),
            "collected_at": self.collected_at.isoformat(),
            "processed_at": self.processed_at.isoformat(),
            "search_phrase": self.search_phrase,
            "analysis": self.analysis.to_dict(),
            "raw_storage_path": self.raw_storage_path,
        }
