from typing import Optional
from pydantic import BaseModel, conint


class CacheItem(BaseModel):
    value: str
    ttl: Optional[conint(gt=0)] = None
