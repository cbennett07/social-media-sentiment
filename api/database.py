from contextlib import contextmanager
from datetime import datetime, date
import psycopg2
from psycopg2.extras import RealDictCursor


class APIDatabase:
    """Database client for API queries."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string

    @contextmanager
    def _get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
        finally:
            conn.close()

    def health_check(self) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception:
            return False

    def get_searches(self) -> list[dict]:
        """Get summary of all search phrases."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        search_phrase as phrase,
                        COUNT(*) as total_items,
                        MIN(collected_at) as first_collected,
                        MAX(collected_at) as last_collected,
                        AVG(sentiment_score) as avg_sentiment_score
                    FROM processed_items
                    GROUP BY search_phrase
                    ORDER BY last_collected DESC
                """)
                results = cur.fetchall()

                # Get sentiment distribution for each phrase
                for row in results:
                    cur.execute("""
                        SELECT sentiment, COUNT(*) as count
                        FROM processed_items
                        WHERE search_phrase = %s
                        GROUP BY sentiment
                    """, (row["phrase"],))
                    dist = {r["sentiment"]: r["count"] for r in cur.fetchall()}
                    row["sentiment_distribution"] = dist

                return [dict(r) for r in results]

    def get_items(
        self,
        search_phrase: str | None = None,
        source_type: str | None = None,
        sentiment: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[dict], int]:
        """Get paginated items with filters."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build WHERE clause
                conditions = []
                params = []

                if search_phrase:
                    conditions.append("search_phrase = %s")
                    params.append(search_phrase)
                if source_type:
                    conditions.append("source_type = %s")
                    params.append(source_type)
                if sentiment:
                    conditions.append("sentiment = %s")
                    params.append(sentiment)
                if start_date:
                    conditions.append("published_at >= %s")
                    params.append(start_date)
                if end_date:
                    conditions.append("published_at <= %s")
                    params.append(end_date)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                # Get total count
                cur.execute(
                    f"SELECT COUNT(*) FROM processed_items {where_clause}",
                    params
                )
                total = cur.fetchone()["count"]

                # Get paginated items
                offset = (page - 1) * page_size
                cur.execute(f"""
                    SELECT
                        id, source_type, source_name, url, title,
                        published_at, sentiment, sentiment_score, summary
                    FROM processed_items
                    {where_clause}
                    ORDER BY published_at DESC
                    LIMIT %s OFFSET %s
                """, params + [page_size, offset])

                items = [dict(r) for r in cur.fetchall()]
                return items, total

    def get_item(self, item_id: str) -> dict | None:
        """Get a single item with full details."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT
                        id, source_type, source_name, url, title, content,
                        author, published_at, collected_at, processed_at,
                        search_phrase, analysis
                    FROM processed_items
                    WHERE id = %s
                """, (item_id,))
                row = cur.fetchone()

                if not row:
                    return None

                result = dict(row)

                # Parse the JSONB analysis field
                analysis = result["analysis"]
                result["analysis"] = {
                    "themes": analysis.get("themes", []),
                    "sentiment": analysis.get("sentiment"),
                    "sentiment_score": analysis.get("sentiment_score"),
                    "summary": analysis.get("summary"),
                    "key_points": analysis.get("key_points", []),
                    "entities": analysis.get("entities", []),
                }

                return result

    def get_themes(
        self,
        search_phrase: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 20
    ) -> list[dict]:
        """Get aggregated themes."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conditions = []
                params = []

                if search_phrase:
                    conditions.append("p.search_phrase = %s")
                    params.append(search_phrase)
                if start_date:
                    conditions.append("p.published_at >= %s")
                    params.append(start_date)
                if end_date:
                    conditions.append("p.published_at <= %s")
                    params.append(end_date)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                cur.execute(f"""
                    SELECT
                        t.name,
                        COUNT(*) as count,
                        AVG(t.confidence) as avg_confidence,
                        ARRAY_AGG(DISTINCT p.source_name) as sources
                    FROM themes t
                    JOIN processed_items p ON t.item_id = p.id
                    {where_clause}
                    GROUP BY t.name
                    ORDER BY count DESC
                    LIMIT %s
                """, params + [limit])

                return [dict(r) for r in cur.fetchall()]

    def get_sentiment_over_time(
        self,
        search_phrase: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        granularity: str = "day"
    ) -> list[dict]:
        """Get sentiment aggregated over time."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conditions = []
                params = []

                if search_phrase:
                    conditions.append("search_phrase = %s")
                    params.append(search_phrase)
                if start_date:
                    conditions.append("published_at >= %s")
                    params.append(start_date)
                if end_date:
                    conditions.append("published_at <= %s")
                    params.append(end_date)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                # Determine date truncation based on granularity
                trunc_map = {
                    "hour": "hour",
                    "day": "day",
                    "week": "week",
                    "month": "month",
                }
                trunc = trunc_map.get(granularity, "day")

                cur.execute(f"""
                    SELECT
                        DATE_TRUNC(%s, published_at) as date,
                        AVG(sentiment_score) as avg_score,
                        COUNT(*) as count,
                        SUM(CASE WHEN sentiment IN ('positive', 'very_positive') THEN 1 ELSE 0 END) as positive,
                        SUM(CASE WHEN sentiment IN ('negative', 'very_negative') THEN 1 ELSE 0 END) as negative,
                        SUM(CASE WHEN sentiment = 'neutral' THEN 1 ELSE 0 END) as neutral
                    FROM processed_items
                    {where_clause}
                    GROUP BY DATE_TRUNC(%s, published_at)
                    ORDER BY date
                """, [trunc] + params + [trunc])

                results = []
                for row in cur.fetchall():
                    r = dict(row)
                    r["date"] = r["date"].isoformat() if r["date"] else None
                    results.append(r)

                return results

    def get_entities(
        self,
        search_phrase: str | None = None,
        start_date: datetime | None = None,
        end_date: datetime | None = None,
        limit: int = 20
    ) -> list[dict]:
        """Get aggregated entities."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conditions = []
                params = []

                if search_phrase:
                    conditions.append("p.search_phrase = %s")
                    params.append(search_phrase)
                if start_date:
                    conditions.append("p.published_at >= %s")
                    params.append(start_date)
                if end_date:
                    conditions.append("p.published_at <= %s")
                    params.append(end_date)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                cur.execute(f"""
                    SELECT
                        e.name,
                        COUNT(*) as count,
                        AVG(p.sentiment_score) as avg_sentiment_score
                    FROM entities e
                    JOIN processed_items p ON e.item_id = p.id
                    {where_clause}
                    GROUP BY e.name
                    ORDER BY count DESC
                    LIMIT %s
                """, params + [limit])

                return [dict(r) for r in cur.fetchall()]

    def get_source_breakdown(
        self,
        search_phrase: str | None = None
    ) -> list[dict]:
        """Get breakdown by source."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                conditions = []
                params = []

                if search_phrase:
                    conditions.append("search_phrase = %s")
                    params.append(search_phrase)

                where_clause = ""
                if conditions:
                    where_clause = "WHERE " + " AND ".join(conditions)

                cur.execute(f"""
                    SELECT
                        source_type,
                        source_name,
                        COUNT(*) as count,
                        AVG(sentiment_score) as avg_sentiment_score
                    FROM processed_items
                    {where_clause}
                    GROUP BY source_type, source_name
                    ORDER BY count DESC
                """, params)

                return [dict(r) for r in cur.fetchall()]

    def full_text_search(
        self,
        query: str,
        search_phrase: str | None = None,
        page: int = 1,
        page_size: int = 20
    ) -> tuple[list[dict], int]:
        """Full-text search across titles and content."""
        with self._get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Build the search query - handle multi-word searches
                search_terms = query.strip().split()
                tsquery = " & ".join(search_terms)

                conditions = [
                    "(to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '') || ' ' || COALESCE(summary, '')) @@ to_tsquery('english', %s))"
                ]
                params = [tsquery]

                if search_phrase:
                    conditions.append("search_phrase = %s")
                    params.append(search_phrase)

                where_clause = "WHERE " + " AND ".join(conditions)

                # Get total count
                cur.execute(
                    f"SELECT COUNT(*) FROM processed_items {where_clause}",
                    params
                )
                total = cur.fetchone()["count"]

                # Get paginated items with relevance ranking
                offset = (page - 1) * page_size
                cur.execute(f"""
                    SELECT
                        id, source_type, source_name, url, title,
                        published_at, sentiment, sentiment_score, summary,
                        search_phrase,
                        ts_rank(
                            to_tsvector('english', COALESCE(title, '') || ' ' || COALESCE(content, '') || ' ' || COALESCE(summary, '')),
                            to_tsquery('english', %s)
                        ) as relevance
                    FROM processed_items
                    {where_clause}
                    ORDER BY relevance DESC, published_at DESC
                    LIMIT %s OFFSET %s
                """, [tsquery] + params + [page_size, offset])

                items = [dict(r) for r in cur.fetchall()]
                return items, total
