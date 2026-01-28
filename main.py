from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import Settings
from collector.service import CollectorService
from collector.queue import RedisQueueClient
from collector.sources.newsapi import NewsAPISource
from collector.sources.reddit import RedditSource
from collector.sources.rss import RSSSource
from collector.models import SearchRequest


settings = Settings()
app = FastAPI(title="Collector Service")


def build_service() -> CollectorService:
    sources = []

    if settings.newsapi_enabled and settings.newsapi_key:
        sources.append(NewsAPISource(settings.newsapi_key))

    if settings.reddit_enabled and settings.reddit_client_id:
        sources.append(RedditSource(
            client_id=settings.reddit_client_id,
            client_secret=settings.reddit_client_secret,
            user_agent=settings.reddit_user_agent,
            subreddits=settings.reddit_subreddits,
        ))

    if settings.rss_enabled and settings.rss_feeds:
        sources.append(RSSSource(settings.rss_feeds))

    queue = RedisQueueClient(settings.redis_url)

    return CollectorService(sources, queue, settings.queue_topic)


service = build_service()


class CollectRequest(BaseModel):
    phrase: str
    start_date: datetime | None = None
    end_date: datetime | None = None
    sources: list[str] | None = None
    job_id: str | None = None


@app.post("/collect")
def collect(req: CollectRequest):
    """Trigger a collection run."""
    search = SearchRequest(
        phrase=req.phrase,
        start_date=req.start_date or datetime.now() - timedelta(days=7),
        end_date=req.end_date or datetime.now(),
        job_id=req.job_id or f"manual-{datetime.now().timestamp()}",
        sources=req.sources,
    )

    stats = service.collect(search)
    return {"status": "completed", "stats": stats}


@app.get("/health")
def health():
    """Health check endpoint."""
    status = service.health()
    healthy = status["queue"] and all(status["sources"].values())
    if not healthy:
        raise HTTPException(status_code=503, detail=status)
    return status
