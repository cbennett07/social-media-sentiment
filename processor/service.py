import json
import logging
from datetime import datetime
from processor.models import ProcessedItem
from processor.queue import QueueConsumer
from processor.llm.base import LLMClient
from processor.storage.base import ObjectStorage
from processor.database.postgres import PostgresDatabase

logger = logging.getLogger(__name__)


class ProcessorService:
    """Orchestrates content processing: consume, analyze, store."""

    def __init__(
        self,
        queue: QueueConsumer,
        llm: LLMClient,
        storage: ObjectStorage,
        database: PostgresDatabase,
        topic: str = "raw_content",
        skip_existing: bool = True
    ):
        self.queue = queue
        self.llm = llm
        self.storage = storage
        self.database = database
        self.topic = topic
        self.skip_existing = skip_existing

    def process_batch(self, batch_size: int = 10) -> dict:
        """
        Process a batch of items from the queue.

        Returns summary stats.
        """
        stats = {
            "processed": 0,
            "skipped": 0,
            "errors": []
        }

        for raw_item in self.queue.consume(self.topic, batch_size):
            try:
                item_id = raw_item.get("id")

                # Skip if already processed
                if self.skip_existing and self.database.exists(item_id):
                    logger.info(f"Skipping already processed item: {item_id}")
                    stats["skipped"] += 1
                    continue

                processed = self._process_item(raw_item)
                self.database.insert(processed)
                stats["processed"] += 1
                logger.info(f"Processed item: {item_id}")

            except Exception as e:
                logger.error(f"Error processing item: {e}")
                stats["errors"].append({
                    "item_id": raw_item.get("id", "unknown"),
                    "error": str(e)
                })

        return stats

    def _process_item(self, raw_item: dict) -> ProcessedItem:
        """Process a single item."""
        item_id = raw_item["id"]

        # Store raw content
        raw_path = f"raw/{raw_item['source_type']}/{item_id}.json"
        self.storage.put(raw_path, json.dumps(raw_item))

        # Run LLM analysis
        analysis = self.llm.analyze(
            title=raw_item.get("title", ""),
            content=raw_item.get("content", ""),
            search_phrase=raw_item.get("search_phrase", "")
        )

        # Build processed item
        return ProcessedItem(
            id=item_id,
            source_type=raw_item["source_type"],
            source_name=raw_item["source_name"],
            url=raw_item["url"],
            title=raw_item.get("title", ""),
            content=raw_item.get("content", ""),
            author=raw_item.get("author"),
            published_at=datetime.fromisoformat(raw_item["published_at"]),
            collected_at=datetime.fromisoformat(raw_item["collected_at"]),
            processed_at=datetime.now(),
            search_phrase=raw_item["search_phrase"],
            analysis=analysis,
            raw_storage_path=raw_path
        )

    def process_continuous(self, batch_size: int = 10) -> None:
        """Continuously process items until interrupted."""
        logger.info("Starting continuous processing...")
        total_processed = 0
        total_errors = 0

        try:
            while True:
                stats = self.process_batch(batch_size)
                total_processed += stats["processed"]
                total_errors += len(stats["errors"])

                if stats["processed"] == 0 and stats["skipped"] == 0:
                    logger.info("No items in queue, waiting...")

        except KeyboardInterrupt:
            logger.info(
                f"Stopping. Total processed: {total_processed}, errors: {total_errors}"
            )

    def health(self) -> dict:
        """Check health of all components.

        Note: LLM and storage checks are skipped for startup probes
        as they can be slow or require external API calls.
        """
        return {
            "queue": self.queue.health_check(),
            "database": self.database.health_check(),
        }
