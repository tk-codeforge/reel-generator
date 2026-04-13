import asyncio
import time

class RateLimiter:
    """Simple token-bucket rate limiter for API calls."""
    def __init__(self, calls_per_second: float = 2.0):
        self.interval = 1.0 / calls_per_second
        self._last_call = 0.0

    async def wait(self):
        now = time.monotonic()
        elapsed = now - self._last_call
        if elapsed < self.interval:
            await asyncio.sleep(self.interval - elapsed)
        self._last_call = time.monotonic()

youtube_limiter = RateLimiter(calls_per_second=2.0)
