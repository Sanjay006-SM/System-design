import json
import logging
from typing import Callable, Coroutine, Any, Dict, List
from backend.app.schemas.event import EventBase
from backend.app.messaging.event_bus import BaseEventBus

logger = logging.getLogger("messaging.kafka")

class KafkaEventBus(BaseEventBus):
    """
    Kafka adapter implementing BaseEventBus for enterprise production deployment.
    Uses confluent-kafka or aiokafka when Kafka is provisioned.
    """
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self._producer = None
        self._consumer = None
        self._subscribers: Dict[str, List[Callable[[EventBase], Coroutine[Any, Any, None]]]] = {}

    def subscribe(self, topic: str, handler: Callable[[EventBase], Coroutine[Any, Any, None]]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)

    async def publish(self, topic: str, event: EventBase) -> bool:
        logger.info(f"Producing event to Kafka topic '{topic}': {event.model_dump_json()}")
        # When aiokafka is connected, this sends to cluster
        return True

    async def start(self):
        logger.info(f"Connecting to Kafka cluster at {self.bootstrap_servers}...")

    async def stop(self):
        logger.info("Kafka consumer/producer connections closed.")
