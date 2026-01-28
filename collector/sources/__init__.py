from collector.sources.base import SourceAdapter
from collector.sources.newsapi import NewsAPISource
from collector.sources.reddit import RedditSource
from collector.sources.rss import RSSSource

__all__ = ["SourceAdapter", "NewsAPISource", "RedditSource", "RSSSource"]
