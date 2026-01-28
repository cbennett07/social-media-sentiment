from datetime import datetime
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from api.config import APISettings
from api.database import APIDatabase
from api.models import (
    ItemResponse,
    ItemSummary,
    SearchSummary,
    ThemeAggregation,
    SentimentOverTime,
    EntityAggregation,
    PaginatedResponse,
)

settings = APISettings()
app = FastAPI(
    title="Sentiment Analysis API",
    description="API for querying social media and news sentiment analysis results",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy database initialization
_db: APIDatabase | None = None


def get_db() -> APIDatabase:
    global _db
    if _db is None:
        _db = APIDatabase(settings.database_url)
    return _db


@app.get("/health")
def health():
    """Health check endpoint."""
    db = get_db()
    if not db.health_check():
        raise HTTPException(status_code=503, detail={"database": False})
    return {"database": True}


@app.get("/searches", response_model=list[SearchSummary])
def list_searches():
    """
    List all search phrases with summary statistics.

    Returns aggregated data for each unique search phrase including
    total items, date range, and sentiment distribution.
    """
    db = get_db()
    return db.get_searches()


@app.get("/items")
def list_items(
    search_phrase: str | None = Query(None, description="Filter by search phrase"),
    source_type: str | None = Query(None, description="Filter by source type (newsapi, reddit, rss)"),
    sentiment: str | None = Query(None, description="Filter by sentiment"),
    start_date: datetime | None = Query(None, description="Filter by start date"),
    end_date: datetime | None = Query(None, description="Filter by end date"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(None, ge=1, le=100, description="Items per page"),
):
    """
    List processed items with optional filters.

    Supports filtering by search phrase, source type, sentiment, and date range.
    Results are paginated.
    """
    db = get_db()
    ps = min(page_size or settings.default_page_size, settings.max_page_size)

    items, total = db.get_items(
        search_phrase=search_phrase,
        source_type=source_type,
        sentiment=sentiment,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=ps
    )

    total_pages = (total + ps - 1) // ps

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": ps,
        "total_pages": total_pages
    }


@app.get("/items/{item_id}", response_model=ItemResponse)
def get_item(item_id: str):
    """
    Get a single item with full analysis details.

    Returns the complete item including all themes, entities, and analysis.
    """
    db = get_db()
    item = db.get_item(item_id)

    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    return item


@app.get("/themes", response_model=list[ThemeAggregation])
def get_themes(
    search_phrase: str | None = Query(None, description="Filter by search phrase"),
    start_date: datetime | None = Query(None, description="Filter by start date"),
    end_date: datetime | None = Query(None, description="Filter by end date"),
    limit: int = Query(20, ge=1, le=100, description="Maximum themes to return"),
):
    """
    Get aggregated themes across all items.

    Themes are ranked by frequency. Includes count, average confidence,
    and which sources contributed to each theme.
    """
    db = get_db()
    return db.get_themes(
        search_phrase=search_phrase,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


@app.get("/sentiment/timeline", response_model=list[SentimentOverTime])
def get_sentiment_timeline(
    search_phrase: str | None = Query(None, description="Filter by search phrase"),
    start_date: datetime | None = Query(None, description="Filter by start date"),
    end_date: datetime | None = Query(None, description="Filter by end date"),
    granularity: str = Query("day", description="Time granularity: hour, day, week, month"),
):
    """
    Get sentiment trends over time.

    Returns aggregated sentiment scores and counts bucketed by the specified
    time granularity.
    """
    if granularity not in ["hour", "day", "week", "month"]:
        raise HTTPException(
            status_code=400,
            detail="Granularity must be one of: hour, day, week, month"
        )

    db = get_db()
    return db.get_sentiment_over_time(
        search_phrase=search_phrase,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity
    )


@app.get("/entities", response_model=list[EntityAggregation])
def get_entities(
    search_phrase: str | None = Query(None, description="Filter by search phrase"),
    start_date: datetime | None = Query(None, description="Filter by start date"),
    end_date: datetime | None = Query(None, description="Filter by end date"),
    limit: int = Query(20, ge=1, le=100, description="Maximum entities to return"),
):
    """
    Get aggregated entities (people, organizations, places).

    Entities are ranked by frequency. Includes count and average sentiment
    score for content mentioning each entity.
    """
    db = get_db()
    return db.get_entities(
        search_phrase=search_phrase,
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )


@app.get("/sources")
def get_sources(
    search_phrase: str | None = Query(None, description="Filter by search phrase"),
):
    """
    Get breakdown of items by source.

    Returns count and average sentiment for each source type and name.
    """
    db = get_db()
    return db.get_source_breakdown(search_phrase=search_phrase)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8082)
