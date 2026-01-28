from abc import ABC, abstractmethod
import redis


class QueueClient(ABC):
    """Abstract queue interface."""

    @abstractmethod
    def publish(self, topic: str, message: str) -> None:
        pass

    @abstractmethod
    def health_check(self) -> bool:
        pass


class RedisQueueClient(QueueClient):
    """Redis-based queue using lists (simple) or streams (if you need consumer groups)."""

    def __init__(self, url: str, use_streams: bool = False):
        self.client = redis.from_url(url)
        self.use_streams = use_streams

    def publish(self, topic: str, message: str) -> None:
        if self.use_streams:
            self.client.xadd(topic, {"data": message})
        else:
            self.client.rpush(topic, message)

    def health_check(self) -> bool:
        try:
            return self.client.ping()
        except Exception:
            return False
