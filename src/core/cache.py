import redis.asyncio as redis
import json
from src.config import settings
from typing import Dict, Any, Optional

class RedisCache:
    def __init__(self):
        self.redis = redis.from_url(settings.REDIS_URL, decode_responses=True)

    async def get_provider_baseline(self, tenant_id: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves the 30-day behavioral baseline for a provider.
        """
        key = f"fwa:{tenant_id}:provider:{provider_id}:baseline"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def set_provider_baseline(self, tenant_id: str, provider_id: str, baseline: Dict[str, Any], ttl: int = 86400):
        """
        Stores a provider baseline. Default TTL is 24 hours.
        """
        key = f"fwa:{tenant_id}:provider:{provider_id}:baseline"
        await self.redis.set(key, json.dumps(baseline), ex=ttl)

    async def get_provider_recent_stats(self, tenant_id: str, provider_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves rolling window stats for the last 7 days.
        """
        key = f"fwa:{tenant_id}:provider:{provider_id}:recent"
        data = await self.redis.get(key)
        if data:
            return json.loads(data)
        return None

    async def close(self):
        await self.redis.close()
