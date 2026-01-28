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
        "Reuters World": "https://feeds.reuters.com/reuters/worldNews",
        "BBC News": "http://feeds.bbci.co.uk/news/rss.xml",
    }

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
