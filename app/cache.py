import asyncio
import time
from collections import OrderedDict
from typing import Any, Optional, Dict, List


class LRUCache:
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be a positive integer")
        self.capacity = capacity
        self.cache: OrderedDict[str, Any] = OrderedDict()
        self.expiration_times: Dict[str, float] = {}
        self.lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        async with self.lock:
            if key not in self.cache:
                return None
            current_time = time.time()
            expiration = self.expiration_times.get(key)
            if expiration is not None and current_time > expiration:
                del self.cache[key]
                del self.expiration_times[key]
                return None
            self.cache.move_to_end(key)
            return self.cache[key]

    async def put(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        async with self.lock:
            current_time = time.time()
            existed = False
            if key in self.cache:
                expiration = self.expiration_times.get(key)
                if expiration is None or current_time <= expiration:
                    existed = True
                else:
                    del self.cache[key]
                    del self.expiration_times[key]

            expiration_time = current_time + ttl if ttl is not None else None
            if key in self.cache:
                self.cache.pop(key)
            self.cache[key] = value
            if expiration_time is not None:
                self.expiration_times[key] = expiration_time
            else:
                self.expiration_times.pop(key, None)

            if len(self.cache) > self.capacity:
                oldest_key = next(iter(self.cache))
                del self.cache[oldest_key]
                self.expiration_times.pop(oldest_key, None)

            return existed

    async def delete(self, key: str) -> bool:
        async with self.lock:
            if key in self.cache:
                del self.cache[key]
                self.expiration_times.pop(key, None)
                return True
            return False

    async def get_stats(self) -> dict:
        async with self.lock:
            return {
                "size": len(self.cache),
                "capacity": self.capacity,
                "items": list(self.cache.keys())[::-1]
            }
