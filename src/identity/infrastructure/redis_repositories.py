import json
from redis.asyncio import Redis
from typing import Any

from src.identity.application.interfaces import ICacheRepository


class RedisCacheRepository(ICacheRepository):
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    async def get(self, key:str) -> Any | None:
        data = await self.redis.get(key)
        if not data:
            return None

        try:
            return json.loads(data)
        except json.JSONDecodeError:
            return data
        
    async def set(self, key: str, value:Any, ttl_second: int = 600) -> None:
        json_data = json.dumps(value, default=str)
        await self.redis.set(key, json_data, ex=ttl_second)

    async def delete(self, key: str) -> None:
        await self.redis.delete(key)
        




