import time
import fnmatch
from typing import Optional, Any, Dict
from backend.app.cache.cache_interface import BaseCache

class InMemoryCache(BaseCache):
    def __init__(self):
        # Dict storing key -> (value, expire_timestamp_or_none)
        self._store: Dict[str, tuple[Any, Optional[float]]] = {}

    async def get(self, key: str) -> Optional[Any]:
        if key not in self._store:
            return None
        value, expire_at = self._store[key]
        if expire_at is not None and time.time() > expire_at:
            del self._store[key]
            return None
        return value

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        expire_at = time.time() + ttl if ttl else None
        self._store[key] = (value, expire_at)
        return True

    async def delete(self, key: str) -> bool:
        if key in self._store:
            del self._store[key]
            return True
        return False

    async def delete_pattern(self, pattern: str) -> int:
        keys_to_delete = [
            k for k in self._store.keys()
            if fnmatch.fnmatch(k, pattern)
        ]
        for k in keys_to_delete:
            del self._store[k]
        return len(keys_to_delete)

    async def ping(self) -> bool:
        return True
