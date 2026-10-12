from backend.app.core.config import settings
from backend.app.messaging.event_bus import BaseEventBus
from backend.app.messaging.memory_queue import LocalAsyncEventBus
from backend.app.messaging.kafka_adapter import KafkaEventBus

_event_bus_instance = None

def get_event_bus() -> BaseEventBus:
    global _event_bus_instance
    if _event_bus_instance is None:
        if settings.KAFKA_ENABLED:
            _event_bus_instance = KafkaEventBus(settings.KAFKA_BOOTSTRAP_SERVERS)
        else:
            _event_bus_instance = LocalAsyncEventBus()
    return _event_bus_instance
