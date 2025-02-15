from fastapi import FastAPI, status, HTTPException
from app.cache import LRUCache
from app.config import Settings
from app.middleware import log_middleware
from app.models import CacheItem

app = FastAPI()
app.middleware("http")(log_middleware)

settings = Settings()
cache = LRUCache(settings.cache_capacity)


@app.get("/cache/stats")
async def get_stats():
    return await cache.get_stats()


@app.get("/cache/{key}")
async def get_cache(key: str):
    value = await cache.get(key)
    if value is None:
        raise HTTPException(status_code=404, detail="Key not found or TTL expired")
    return {"value": value}


@app.put("/cache/{key}", status_code=status.HTTP_200_OK)
async def put_cache(key: str, item: CacheItem):
    try:
        existed = await cache.put(key, item.value, item.ttl)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return status.HTTP_201_CREATED if not existed else status.HTTP_200_OK


@app.delete("/cache/{key}", status_code=204)
async def delete_cache(key: str):
    deleted = await cache.delete(key)
    if not deleted:
        raise HTTPException(status_code=404, detail="Key not found")
    return status.HTTP_204_NO_CONTENT



