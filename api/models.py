from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class Sentiment(str, Enum):
    VERY_NEGATIVE = "very_negative"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"
    POSITIVE = "positive"
    VERY_POSITIVE = "very_positive"


class ThemeResponse(BaseModel):
    name: str
    confidence: float
    keywords: list[str]


class AnalysisResponse(BaseModel):
    themes: list[ThemeResponse]
    sentiment: Sentiment
    sentiment_score: float
    summary: str
    key_points: list[str]
    entities: list[str]


class ItemResponse(BaseModel):
    id: str
    source_type: str
    source_name: str
    url: str
    title: str
    content: str | None
    author: str | None
    published_at: datetime
    collected_at: datetime
    processed_at: datetime
    search_phrase: str
    analysis: AnalysisResponse


class ItemSummary(BaseModel):
    id: str
    source_type: str
    source_name: str
    url: str
    title: str
    published_at: datetime
    sentiment: Sentiment
    sentiment_score: float
    summary: str


class SearchSummary(BaseModel):
    phrase: str
    total_items: int
    first_collected: datetime | None
    last_collected: datetime | None
    first_published: datetime | None
    last_published: datetime | None
    avg_sentiment_score: float
    sentiment_distribution: dict[str, int]


class ThemeAggregation(BaseModel):
    name: str
    count: int
    avg_confidence: float
    sources: list[str]


class SentimentOverTime(BaseModel):
    date: str
    avg_score: float
    count: int
    positive: int
    negative: int
    neutral: int


class EntityAggregation(BaseModel):
    name: str
    count: int
    avg_sentiment_score: float


class PaginatedResponse(BaseModel):
    items: list
    total: int
    page: int
    page_size: int
    total_pages: int
