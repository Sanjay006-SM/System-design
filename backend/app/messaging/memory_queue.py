import asyncio
import logging
from typing import Callable, Coroutine, Any, Dict, List
from backend.app.schemas.event import EventBase
from backend.app.messaging.event_bus import BaseEventBus

logger = logging.getLogger("messaging.memory_queue")

class LocalAsyncEventBus(BaseEventBus):
    """
    In-process asynchronous event bus using asyncio.Queue for local MVP development.
    Simulates Kafka topic publishing and async consumer processing.
    """
    def __init__(self):
        self._subscribers: Dict[str, List[Callable[[EventBase], Coroutine[Any, Any, None]]]] = {}
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: asyncio.Task = None
        self._running: bool = False

    def subscribe(self, topic: str, handler: Callable[[EventBase], Coroutine[Any, Any, None]]):
        if topic not in self._subscribers:
            self._subscribers[topic] = []
        self._subscribers[topic].append(handler)
        logger.info(f"Subscribed handler {handler.__name__} to topic '{topic}'")

    async def publish(self, topic: str, event: EventBase) -> bool:
        logger.info(f"Publishing event {event.event_type} (id: {event.event_id}) to topic '{topic}'")
        await self._queue.put((topic, event))
        return True

    async def _process_events(self):
        while self._running:
            try:
                topic, event = await self._queue.get()
                handlers = self._subscribers.get(topic, [])
                for handler in handlers:
                    try:
                        await handler(event)
                    except Exception as e:
                        logger.exception(f"Error handling event {event.event_id} in {handler.__name__}: {e}")
                self._queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.exception(f"Error in event bus worker loop: {e}")

    async def start(self):
        if not self._running:
            self._running = True
            self._worker_task = asyncio.create_task(self._process_events())
            logger.info("Local Async Event Bus started.")

    async def stop(self):
        if self._running:
            self._running = False
            if self._worker_task:
                self._worker_task.cancel()
                try:
                    await self._worker_task
                except asyncio.CancelledError:
                    pass
            logger.info("Local Async Event Bus stopped.")
