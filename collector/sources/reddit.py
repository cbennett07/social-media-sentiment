import httpx
from datetime import datetime
from typing import Iterator
from collector.models import CollectedItem, SearchRequest, SourceType
from collector.sources.base import SourceAdapter


class RedditSource(SourceAdapter):
    """Adapter for Reddit API."""

    AUTH_URL = "https://www.reddit.com/api/v1/access_token"
    BASE_URL = "https://oauth.reddit.com"

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        user_agent: str,
        subreddits: list[str] | None = None
    ):
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_agent = user_agent
        self.subreddits = subreddits or ["all"]
        self._token: str | None = None
        self._client: httpx.Client | None = None

    @property
    def source_type(self) -> str:
        return SourceType.REDDIT

    @property
    def name(self) -> str:
        return "Reddit"

    @property
    def client(self) -> httpx.Client:
        if self._client is None:
            self._authenticate()
        return self._client

    def _authenticate(self):
        """Get OAuth token using client credentials flow."""
        auth_client = httpx.Client()
        response = auth_client.post(
            self.AUTH_URL,
            auth=(self.client_id, self.client_secret),
            data={"grant_type": "client_credentials"},
            headers={"User-Agent": self.user_agent}
        )
        response.raise_for_status()
        self._token = response.json()["access_token"]

        self._client = httpx.Client(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {self._token}",
                "User-Agent": self.user_agent
            }
        )

    def search(self, request: SearchRequest) -> Iterator[CollectedItem]:
        for subreddit in self.subreddits:
            yield from self._search_subreddit(subreddit, request)

    def _search_subreddit(
        self, subreddit: str, request: SearchRequest
    ) -> Iterator[CollectedItem]:
        after = None

        while True:
            params = {
                "q": request.phrase,
                "restrict_sr": True if subreddit != "all" else False,
                "sort": "new",
                "t": "all",
                "limit": 100,
            }
            if after:
                params["after"] = after

            response = self.client.get(
                f"{self.BASE_URL}/r/{subreddit}/search",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            posts = data["data"]["children"]
            if not posts:
                break

            for post in posts:
                item = self._to_collected_item(post["data"], request.phrase)

                # Filter by date range (Reddit API doesn't support date filtering)
                if item.published_at < request.start_date:
                    return  # Posts are sorted by new, so we can stop
                if item.published_at <= request.end_date:
                    yield item

            after = data["data"].get("after")
            if not after:
                break

    def _to_collected_item(self, post: dict, phrase: str) -> CollectedItem:
        return CollectedItem(
            source_type=self.source_type,
            source_name=f"r/{post['subreddit']}",
            external_id=post["id"],
            url=f"https://reddit.com{post['permalink']}",
            title=post.get("title", ""),
            content=post.get("selftext", ""),
            author=post.get("author"),
            published_at=datetime.fromtimestamp(post["created_utc"]),
            collected_at=datetime.now(),
            search_phrase=phrase,
            metadata={
                "score": post.get("score"),
                "num_comments": post.get("num_comments"),
                "subreddit": post.get("subreddit"),
                "is_self": post.get("is_self"),
                "link_url": post.get("url") if not post.get("is_self") else None,
            }
        )

    def health_check(self) -> bool:
        try:
            response = self.client.get(f"{self.BASE_URL}/api/v1/me")
            return response.status_code == 200
        except Exception:
            return False
