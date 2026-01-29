import httpx
import feedparser
from datetime import datetime, timezone
from time import mktime
from typing import Iterator
from collector.models import CollectedItem, SearchRequest, SourceType
from collector.sources.base import SourceAdapter


class RSSSource(SourceAdapter):
    """Adapter for RSS/Atom feeds."""

    def __init__(self, feeds: dict[str, str]):
        """
        Args:
            feeds: Mapping of feed name to URL, e.g.:
                   {"Reuters World": "https://feeds.reuters.com/..."}
        """
        self.feeds = feeds
        self.client = httpx.Client(timeout=30.0, follow_redirects=True)

    @property
    def source_type(self) -> str:
        return SourceType.RSS

    @property
    def name(self) -> str:
        return "RSS"

    def search(self, request: SearchRequest) -> Iterator[CollectedItem]:
        phrase_lower = request.phrase.lower()

        for feed_name, feed_url in self.feeds.items():
            try:
                yield from self._search_feed(
                    feed_name, feed_url, phrase_lower, request
                )
            except Exception as e:
                # Log but don't fail entire collection
                print(f"Error fetching feed {feed_name}: {e}")

    def _search_feed(
        self,
        feed_name: str,
        feed_url: str,
        phrase_lower: str,
        request: SearchRequest
    ) -> Iterator[CollectedItem]:
        response = self.client.get(feed_url)
        response.raise_for_status()

        feed = feedparser.parse(response.text)

        for entry in feed.entries:
            # Check if phrase appears in title or summary
            title = entry.get("title", "")
            summary = entry.get("summary", "")

            if phrase_lower not in title.lower() and phrase_lower not in summary.lower():
                continue

            item = self._to_collected_item(entry, feed_name, request.phrase)

            # Filter by date range
            if request.start_date <= item.published_at <= request.end_date:
                yield item

    def _to_collected_item(
        self, entry: dict, feed_name: str, phrase: str
    ) -> CollectedItem:
        # Parse published date - feedparser normalizes to struct_time
        # Use UTC timezone for consistent comparison with request dates
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published = datetime.fromtimestamp(mktime(entry.published_parsed), tz=timezone.utc)
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published = datetime.fromtimestamp(mktime(entry.updated_parsed), tz=timezone.utc)
        else:
            published = datetime.now(timezone.utc)

        return CollectedItem(
            source_type=self.source_type,
            source_name=feed_name,
            external_id=entry.get("id", entry.get("link", "")),
            url=entry.get("link", ""),
            title=entry.get("title", ""),
            content=entry.get("summary", ""),
            author=entry.get("author"),
            published_at=published,
            collected_at=datetime.now(timezone.utc),
            search_phrase=phrase,
            metadata={
                "tags": [t.term for t in entry.get("tags", [])],
            }
        )

    def health_check(self) -> bool:
        # Check first feed is reachable
        if not self.feeds:
            return False
        try:
            url = list(self.feeds.values())[0]
            response = self.client.head(url)
            return response.status_code == 200
        except Exception:
            return False
