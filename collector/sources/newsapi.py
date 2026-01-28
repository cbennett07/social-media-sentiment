import httpx
from datetime import datetime
from typing import Iterator
from collector.models import CollectedItem, SearchRequest, SourceType
from collector.sources.base import SourceAdapter


class NewsAPISource(SourceAdapter):
    """Adapter for NewsAPI.org."""

    BASE_URL = "https://newsapi.org/v2"

    def __init__(self, api_key: str, page_size: int = 100):
        self.api_key = api_key
        self.page_size = page_size
        self.client = httpx.Client(
            timeout=30.0,
            headers={"X-Api-Key": self.api_key}
        )

    @property
    def source_type(self) -> str:
        return SourceType.NEWS_API

    @property
    def name(self) -> str:
        return "NewsAPI"

    def search(self, request: SearchRequest) -> Iterator[CollectedItem]:
        page = 1
        total_results = None

        while True:
            params = {
                "q": request.phrase,
                "from": request.start_date.strftime("%Y-%m-%d"),
                "to": request.end_date.strftime("%Y-%m-%d"),
                "pageSize": self.page_size,
                "page": page,
                "sortBy": "publishedAt",
                "language": "en",
            }

            response = self.client.get(f"{self.BASE_URL}/everything", params=params)
            response.raise_for_status()
            data = response.json()

            if data["status"] != "ok":
                raise RuntimeError(f"NewsAPI error: {data.get('message', 'Unknown')}")

            if total_results is None:
                total_results = data["totalResults"]

            for article in data["articles"]:
                yield self._to_collected_item(article, request.phrase)

            # Check if we've fetched all available results
            fetched = page * self.page_size
            if fetched >= total_results or not data["articles"]:
                break

            page += 1

    def _to_collected_item(self, article: dict, phrase: str) -> CollectedItem:
        return CollectedItem(
            source_type=self.source_type,
            source_name=article.get("source", {}).get("name", "unknown"),
            external_id=article["url"],  # NewsAPI doesn't provide unique IDs
            url=article["url"],
            title=article.get("title", ""),
            content=article.get("content") or article.get("description") or "",
            author=article.get("author"),
            published_at=datetime.fromisoformat(
                article["publishedAt"].replace("Z", "+00:00")
            ),
            collected_at=datetime.now(),
            search_phrase=phrase,
            metadata={
                "description": article.get("description"),
                "image_url": article.get("urlToImage"),
            }
        )

    def health_check(self) -> bool:
        try:
            response = self.client.get(
                f"{self.BASE_URL}/top-headlines",
                params={"country": "us", "pageSize": 1}
            )
            return response.status_code == 200
        except Exception:
            return False
