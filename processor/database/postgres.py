import json
from datetime import datetime
from contextlib import contextmanager
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from processor.models import ProcessedItem


class PostgresDatabase:
    """PostgreSQL database client for storing processed items."""

    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self._ensure_schema()

    @contextmanager
    def _get_connection(self):
        conn = psycopg2.connect(self.connection_string)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _ensure_schema(self):
        """Create tables if they don't exist."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS processed_items (
                        id VARCHAR(64) PRIMARY KEY,
                        source_type VARCHAR(32) NOT NULL,
                        source_name VARCHAR(128) NOT NULL,
                        url TEXT NOT NULL,
                        title TEXT NOT NULL,
                        content TEXT,
                        author VARCHAR(256),
                        published_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        collected_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        processed_at TIMESTAMP WITH TIME ZONE NOT NULL,
                        search_phrase VARCHAR(256) NOT NULL,
                        raw_storage_path TEXT NOT NULL,
                        sentiment VARCHAR(32) NOT NULL,
                        sentiment_score FLOAT NOT NULL,
                        summary TEXT,
                        analysis JSONB NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_processed_items_search_phrase
                        ON processed_items(search_phrase);
                    CREATE INDEX IF NOT EXISTS idx_processed_items_published_at
                        ON processed_items(published_at);
                    CREATE INDEX IF NOT EXISTS idx_processed_items_sentiment
                        ON processed_items(sentiment);
                    CREATE INDEX IF NOT EXISTS idx_processed_items_source_type
                        ON processed_items(source_type);

                    CREATE TABLE IF NOT EXISTS themes (
                        id SERIAL PRIMARY KEY,
                        item_id VARCHAR(64) REFERENCES processed_items(id),
                        name VARCHAR(128) NOT NULL,
                        confidence FLOAT NOT NULL,
                        keywords TEXT[] NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_themes_item_id ON themes(item_id);
                    CREATE INDEX IF NOT EXISTS idx_themes_name ON themes(name);

                    CREATE TABLE IF NOT EXISTS entities (
                        id SERIAL PRIMARY KEY,
                        item_id VARCHAR(64) REFERENCES processed_items(id),
                        name VARCHAR(256) NOT NULL,
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    );

                    CREATE INDEX IF NOT EXISTS idx_entities_item_id ON entities(item_id);
                    CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(name);
                """)

    def insert(self, item: ProcessedItem) -> None:
        """Insert a processed item and its related data."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                # Insert main item
                cur.execute("""
                    INSERT INTO processed_items (
                        id, source_type, source_name, url, title, content,
                        author, published_at, collected_at, processed_at,
                        search_phrase, raw_storage_path, sentiment,
                        sentiment_score, summary, analysis
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    ON CONFLICT (id) DO UPDATE SET
                        processed_at = EXCLUDED.processed_at,
                        sentiment = EXCLUDED.sentiment,
                        sentiment_score = EXCLUDED.sentiment_score,
                        summary = EXCLUDED.summary,
                        analysis = EXCLUDED.analysis
                """, (
                    item.id,
                    item.source_type,
                    item.source_name,
                    item.url,
                    item.title,
                    item.content,
                    item.author,
                    item.published_at,
                    item.collected_at,
                    item.processed_at,
                    item.search_phrase,
                    item.raw_storage_path,
                    item.analysis.sentiment.value,
                    item.analysis.sentiment_score,
                    item.analysis.summary,
                    Json(item.analysis.to_dict())
                ))

                # Delete existing themes/entities for this item (for reprocessing)
                cur.execute("DELETE FROM themes WHERE item_id = %s", (item.id,))
                cur.execute("DELETE FROM entities WHERE item_id = %s", (item.id,))

                # Insert themes
                for theme in item.analysis.themes:
                    cur.execute("""
                        INSERT INTO themes (item_id, name, confidence, keywords)
                        VALUES (%s, %s, %s, %s)
                    """, (item.id, theme.name, theme.confidence, theme.keywords))

                # Insert entities
                for entity in item.analysis.entities:
                    cur.execute("""
                        INSERT INTO entities (item_id, name)
                        VALUES (%s, %s)
                    """, (item.id, entity))

    def exists(self, item_id: str) -> bool:
        """Check if an item has already been processed."""
        with self._get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    "SELECT 1 FROM processed_items WHERE id = %s",
                    (item_id,)
                )
                return cur.fetchone() is not None

    def health_check(self) -> bool:
        try:
            with self._get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute("SELECT 1")
                    return True
        except Exception:
            return False
