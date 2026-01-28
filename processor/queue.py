from abc import ABC, abstractmethod
from typing import Iterator
import json
import redis


class QueueConsumer(ABC):
    """Abstract queue consumer interface."""

    @abstractmethod
    def consume(self, topic: str, batch_size: int = 10) -> Iterator[dict]:
        """
        Consume messages from the queue.

        Yields parsed message dictionaries.
        """
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass


class RedisQueueConsumer(QueueConsumer):
    """Redis-based queue consumer."""

    def __init__(self, url: str, use_streams: bool = False, block_timeout: int = 5):
        self.client = redis.from_url(url)
        self.use_streams = use_streams
        self.block_timeout = block_timeout

    def consume(self, topic: str, batch_size: int = 10) -> Iterator[dict]:
        if self.use_streams:
            yield from self._consume_stream(topic, batch_size)
        else:
            yield from self._consume_list(topic, batch_size)

    def _consume_list(self, topic: str, batch_size: int) -> Iterator[dict]:
        """Consume from Redis list using BLPOP."""
        while True:
            # BLPOP returns (key, value) or None on timeout
            result = self.client.blpop(topic, timeout=self.block_timeout)
            if result is None:
                break  # No more messages within timeout

            _, message = result
            yield json.loads(message)

    def _consume_stream(self, topic: str, batch_size: int) -> Iterator[dict]:
        """Consume from Redis stream."""
        last_id = "0"

        while True:
            # XREAD with block
            results = self.client.xread(
                {topic: last_id},
                count=batch_size,
                block=self.block_timeout * 1000  # milliseconds
            )

            if not results:
                break

            for stream_name, messages in results:
                for message_id, data in messages:
                    last_id = message_id
                    yield json.loads(data[b"data"])

    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False
