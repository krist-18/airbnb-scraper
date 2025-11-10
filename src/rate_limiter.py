thon
from __future__ import annotations

import asyncio
import random
from contextlib import asynccontextmanager
from typing import AsyncIterator

class AsyncRateLimiter:
    """
    Lightweight async rate limiter based on a semaphore and randomized sleep.
    """

    def __init__(self, concurrency: int = 2, min_delay_ms: int = 200, max_delay_ms: int = 800) -> None:
        self._sem = asyncio.Semaphore(max(1, concurrency))