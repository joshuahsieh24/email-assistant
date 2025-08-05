"""Redis-based rate limiting using token bucket algorithm."""

import time
from typing import Optional

import aioredis

from .settings import settings


class RateLimiter:
    """Redis-based rate limiter using token bucket algorithm."""

    def __init__(self, redis_client: aioredis.Redis) -> None:
        """Initialize rate limiter with Redis client."""
        self.redis = redis_client
        self.requests_per_window = settings.rate_limit_requests
        self.window_seconds = settings.rate_limit_window_seconds

    async def is_allowed(self, org_id: str) -> bool:
        """
        Check if request is allowed for the given org.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            True if request is allowed, False otherwise
        """
        key = f"rate_limit:{org_id}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Use Redis pipeline for atomic operations
        pipe = self.redis.pipeline()
        
        # Remove old entries (older than window)
        pipe.zremrangebyscore(key, 0, window_start)
        
        # Count current requests in window
        pipe.zcard(key)
        
        # Add current request timestamp
        pipe.zadd(key, {str(current_time): current_time})
        
        # Set expiry on the key
        pipe.expire(key, self.window_seconds)
        
        # Execute pipeline
        results = await pipe.execute()
        current_requests = results[1]  # zcard result
        
        return current_requests < self.requests_per_window

    async def get_remaining_requests(self, org_id: str) -> int:
        """
        Get remaining requests for the given org.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            Number of remaining requests
        """
        key = f"rate_limit:{org_id}"
        current_time = int(time.time())
        window_start = current_time - self.window_seconds
        
        # Remove old entries
        await self.redis.zremrangebyscore(key, 0, window_start)
        
        # Count current requests
        current_requests = await self.redis.zcard(key)
        
        return max(0, self.requests_per_window - current_requests)

    async def get_reset_time(self, org_id: str) -> Optional[int]:
        """
        Get the time when rate limit resets for the given org.
        
        Args:
            org_id: Organization identifier
            
        Returns:
            Unix timestamp when rate limit resets, or None if no requests
        """
        key = f"rate_limit:{org_id}"
        
        # Get the oldest request in the window
        oldest_request = await self.redis.zrange(key, 0, 0, withscores=True)
        
        if not oldest_request:
            return None
        
        oldest_time = int(oldest_request[0][1])
        return oldest_time + self.window_seconds


class RedisManager:
    """Redis connection manager."""
    
    def __init__(self) -> None:
        """Initialize Redis manager."""
        self.redis: Optional[aioredis.Redis] = None

    async def connect(self) -> None:
        """Connect to Redis."""
        self.redis = aioredis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        await self.redis.ping()

    async def disconnect(self) -> None:
        """Disconnect from Redis."""
        if self.redis:
            await self.redis.close()

    async def is_connected(self) -> bool:
        """Check if Redis is connected."""
        try:
            if self.redis:
                await self.redis.ping()
                return True
        except Exception:
            pass
        return False

    def get_rate_limiter(self) -> RateLimiter:
        """Get rate limiter instance."""
        if not self.redis:
            raise RuntimeError("Redis not connected")
        return RateLimiter(self.redis)


# Global Redis manager
redis_manager = RedisManager() 