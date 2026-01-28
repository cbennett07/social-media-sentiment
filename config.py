from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Queue
    redis_url: str = "redis://localhost:6379"
    queue_topic: str = "raw_content"

    # NewsAPI
    newsapi_key: str | None = None
    newsapi_enabled: bool = True

    # Reddit
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_user_agent: str = "SentimentCollector/1.0"
    reddit_subreddits: list[str] = ["news", "worldnews", "technology"]
    reddit_enabled: bool = True

    # RSS
    rss_enabled: bool = True
    rss_feeds: dict[str, str] = {
        "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
        "BBC Tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "NPR News": "https://feeds.npr.org/1001/rss.xml",
    }

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = "ignore"
