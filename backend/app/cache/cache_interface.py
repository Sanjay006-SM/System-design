from abc import ABC, abstractmethod
from typing import Optional, Any

class BaseCache(ABC):
    @abstractmethod
    async def get(self, key: str) -> Optional[Any]:
        pass

    @abstractmethod
    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        pass

    @abstractmethod
    async def delete(self, key: str) -> bool:
        pass

    @abstractmethod
    async def delete_pattern(self, pattern: str) -> int:
        """Invalidates all keys matching the pattern (e.g., feed:user:101:*)"""
        pass

    @abstractmethod
    async def ping(self) -> bool:
        pass
