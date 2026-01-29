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

    # Twitter/X
    twitter_bearer_token: str | None = None
    twitter_enabled: bool = True
    twitter_max_results: int = 100

    # RSS
    rss_enabled: bool = True
    rss_feeds: dict[str, str] = {
        # === US News ===
        "NPR News": "https://feeds.npr.org/1001/rss.xml",
        "NPR World": "https://feeds.npr.org/1004/rss.xml",
        "NPR Politics": "https://feeds.npr.org/1014/rss.xml",
        "NPR Business": "https://feeds.npr.org/1006/rss.xml",
        "NPR Technology": "https://feeds.npr.org/1019/rss.xml",
        "CBS News": "https://www.cbsnews.com/latest/rss/main",
        "ABC News": "https://abcnews.go.com/abcnews/topstories",
        "PBS NewsHour": "https://www.pbs.org/newshour/feeds/rss/headlines",
        "AP News": "https://rsshub.app/apnews/topics/apf-topnews",
        "USA Today": "http://rssfeeds.usatoday.com/usatoday-NewsTopStories",

        # === UK News ===
        "BBC News": "https://feeds.bbci.co.uk/news/rss.xml",
        "BBC World": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "BBC Tech": "https://feeds.bbci.co.uk/news/technology/rss.xml",
        "BBC Business": "https://feeds.bbci.co.uk/news/business/rss.xml",
        "BBC Science": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
        "The Guardian World": "https://www.theguardian.com/world/rss",
        "The Guardian US": "https://www.theguardian.com/us-news/rss",
        "The Guardian Tech": "https://www.theguardian.com/technology/rss",
        "The Guardian Business": "https://www.theguardian.com/business/rss",
        "Sky News": "https://feeds.skynews.com/feeds/rss/world.xml",

        # === International ===
        "Al Jazeera": "https://www.aljazeera.com/xml/rss/all.xml",
        "France24": "https://www.france24.com/en/rss",
        "DW News": "https://rss.dw.com/rdf/rss-en-all",
        "ABC Australia": "https://www.abc.net.au/news/feed/1948/rss.xml",

        # === Business & Finance ===
        "CNBC Top": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
        "CNBC World": "https://www.cnbc.com/id/100727362/device/rss/rss.html",
        "Bloomberg": "https://feeds.bloomberg.com/markets/news.rss",
        "MarketWatch": "http://feeds.marketwatch.com/marketwatch/topstories",
        "Financial Times": "https://www.ft.com/rss/home",

        # === Tech ===
        "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
        "The Verge": "https://www.theverge.com/rss/index.xml",
        "Wired": "https://www.wired.com/feed/rss",
        "TechCrunch": "https://techcrunch.com/feed/",
        "Engadget": "https://www.engadget.com/rss.xml",
        "Hacker News": "https://hnrss.org/frontpage",
        "MIT Tech Review": "https://www.technologyreview.com/feed/",

        # === Science ===
        "Nature News": "https://www.nature.com/nature.rss",
        "Science Daily": "https://www.sciencedaily.com/rss/all.xml",
        "New Scientist": "https://www.newscientist.com/feed/home/",
        "Phys.org": "https://phys.org/rss-feed/",

        # === Politics ===
        "Politico": "https://www.politico.com/rss/politicopicks.xml",
        "The Hill": "https://thehill.com/feed/",
        "FiveThirtyEight": "https://fivethirtyeight.com/features/feed/",

        # === Social/Aggregators ===
        "Reddit Popular": "https://www.reddit.com/r/popular/.rss",
        "Reddit News": "https://www.reddit.com/r/news/.rss",
        "Reddit World News": "https://www.reddit.com/r/worldnews/.rss",
        "Reddit Technology": "https://www.reddit.com/r/technology/.rss",
    }

    class Config:
        env_file = ".env"
        env_nested_delimiter = "__"
        extra = "ignore"
