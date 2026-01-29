import httpx
from datetime import datetime, timezone
from typing import Iterator
from collector.models import CollectedItem, SearchRequest, SourceType
from collector.sources.base import SourceAdapter


class TwitterSource(SourceAdapter):
    """Adapter for X/Twitter API v2."""

    BASE_URL = "https://api.twitter.com/2"

    def __init__(self, bearer_token: str, max_results: int = 100):
        """
        Args:
            bearer_token: X API Bearer token (from developer portal)
            max_results: Results per request (10-100, default 100)
        """
        self.bearer_token = bearer_token
        self.max_results = min(max(max_results, 10), 100)
        self.client = httpx.Client(
            timeout=30.0,
            headers={"Authorization": f"Bearer {self.bearer_token}"}
        )

    @property
    def source_type(self) -> str:
        return SourceType.TWITTER

    @property
    def name(self) -> str:
        return "Twitter/X"

    def search(self, request: SearchRequest) -> Iterator[CollectedItem]:
        """
        Search recent tweets using X API v2.

        Note: Free tier only allows 1,500 tweets/month.
        Basic tier ($100/month) allows 10,000 tweets/month.
        """
        next_token = None

        while True:
            params = {
                "query": f"{request.phrase} lang:en -is:retweet",
                "max_results": self.max_results,
                "start_time": request.start_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "end_time": request.end_date.strftime("%Y-%m-%dT%H:%M:%SZ"),
                "tweet.fields": "id,text,author_id,created_at,public_metrics,entities",
                "user.fields": "username,name",
                "expansions": "author_id",
            }

            if next_token:
                params["next_token"] = next_token

            response = self.client.get(
                f"{self.BASE_URL}/tweets/search/recent",
                params=params
            )
            response.raise_for_status()
            data = response.json()

            # Handle errors from API
            if "errors" in data and not "data" in data:
                error_msg = data["errors"][0].get("message", "Unknown error")
                raise RuntimeError(f"Twitter API error: {error_msg}")

            # No results
            if "data" not in data:
                break

            # Build user lookup for author info
            users = {}
            if "includes" in data and "users" in data["includes"]:
                for user in data["includes"]["users"]:
                    users[user["id"]] = user

            for tweet in data["data"]:
                author = users.get(tweet.get("author_id"), {})
                yield self._to_collected_item(tweet, author, request.phrase)

            # Check for more pages
            meta = data.get("meta", {})
            next_token = meta.get("next_token")
            if not next_token:
                break

    def _to_collected_item(
        self, tweet: dict, author: dict, phrase: str
    ) -> CollectedItem:
        # Parse created_at timestamp
        created_at = tweet.get("created_at", "")
        if created_at:
            published = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
        else:
            published = datetime.now(timezone.utc)

        # Build tweet URL
        username = author.get("username", "unknown")
        tweet_id = tweet["id"]
        url = f"https://twitter.com/{username}/status/{tweet_id}"

        # Get engagement metrics
        metrics = tweet.get("public_metrics", {})

        return CollectedItem(
            source_type=self.source_type,
            source_name=f"@{username}",
            external_id=tweet_id,
            url=url,
            title="",  # Tweets don't have titles
            content=tweet.get("text", ""),
            author=author.get("name") or username,
            published_at=published,
            collected_at=datetime.now(timezone.utc),
            search_phrase=phrase,
            metadata={
                "username": username,
                "author_id": tweet.get("author_id"),
                "retweet_count": metrics.get("retweet_count", 0),
                "reply_count": metrics.get("reply_count", 0),
                "like_count": metrics.get("like_count", 0),
                "quote_count": metrics.get("quote_count", 0),
                "hashtags": [
                    tag["tag"] for tag in
                    tweet.get("entities", {}).get("hashtags", [])
                ],
                "mentions": [
                    mention["username"] for mention in
                    tweet.get("entities", {}).get("mentions", [])
                ],
            }
        )

    def health_check(self) -> bool:
        """Check if API is accessible with current credentials."""
        try:
            # Use a minimal request to check auth
            response = self.client.get(
                f"{self.BASE_URL}/tweets/search/recent",
                params={"query": "test", "max_results": 10}
            )
            # 200 = OK, 429 = rate limited (but auth works)
            return response.status_code in (200, 429)
        except Exception:
            return False
