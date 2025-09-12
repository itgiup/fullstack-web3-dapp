import logging
import redis.asyncio as redis
from typing import Optional
from app.config import settings

logger = logging.getLogger(__name__)


class RedisConnection:
    def __init__(self):
        self.redis: Optional[redis.Redis] = None

    async def connect(self):
        """Create Redis connection"""
        try:
            self.redis = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
                socket_connect_timeout=5,
                socket_timeout=5
            )
            
            # Test connection
            await self.redis.ping()
            logger.info("Successfully connected to Redis")
            
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis connection closed")

    async def get_redis(self) -> redis.Redis:
        """Get Redis client"""
        if not self.redis:
            await self.connect()
        return self.redis

    async def health_check(self) -> bool:
        """Check Redis health"""
        try:
            if not self.redis:
                return False
            await self.redis.ping()
            return True
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return False


# Global Redis connection instance
redis_conn = RedisConnection()


async def get_redis() -> redis.Redis:
    """Get Redis connection"""
    return await redis_conn.get_redis()


async def connect_to_redis():
    """Connect to Redis"""
    await redis_conn.connect()


async def close_redis_connection():
    """Close Redis connection"""
    await redis_conn.disconnect()


async def check_redis_health() -> bool:
    """Check Redis health"""
    return await redis_conn.health_check()
