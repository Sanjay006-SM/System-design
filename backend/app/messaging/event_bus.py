from abc import ABC, abstractmethod
from typing import Callable, Coroutine, Any, Dict, List
import logging
from backend.app.schemas.event import EventBase

logger = logging.getLogger("messaging.event_bus")

class BaseEventBus(ABC):
    @abstractmethod
    async def publish(self, topic: str, event: EventBase) -> bool:
        pass

    @abstractmethod
    def subscribe(self, topic: str, handler: Callable[[EventBase], Coroutine[Any, Any, None]]):
        pass

    @abstractmethod
    async def start(self):
        pass

    @abstractmethod
    async def stop(self):
        pass
