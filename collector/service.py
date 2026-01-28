from collector.models import SearchRequest
from collector.sources.base import SourceAdapter
from collector.queue import QueueClient


class CollectorService:
    """Orchestrates collection from multiple sources."""

    def __init__(
        self,
        sources: list[SourceAdapter],
        queue: QueueClient,
        topic: str = "raw_content"
    ):
        self.sources = {s.source_type: s for s in sources}
        self.queue = queue
        self.topic = topic

    def collect(self, request: SearchRequest) -> dict:
        """
        Run collection for a search request.

        Returns summary stats.
        """
        stats = {"total": 0, "by_source": {}, "errors": []}

        active_sources = (
            [self.sources[s] for s in request.sources if s in self.sources]
            if request.sources
            else list(self.sources.values())
        )

        for source in active_sources:
            source_count = 0
            try:
                for item in source.search(request):
                    self.queue.publish(self.topic, item.to_json())
                    source_count += 1
            except Exception as e:
                stats["errors"].append({
                    "source": source.name,
                    "error": str(e)
                })

            stats["by_source"][source.name] = source_count
            stats["total"] += source_count

        return stats

    def health(self) -> dict:
        """Check health of all components."""
        return {
            "queue": self.queue.health_check(),
            "sources": {
                name: source.health_check()
                for name, source in self.sources.items()
            }
        }
