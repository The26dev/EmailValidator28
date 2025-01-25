"""SQLite-based rate limiter implementation as an alternative to Redis.

This module provides a SQLite-based rate limiting solution that can be used as a drop-in
replacement for Redis in Windows environments.
"""
import sqlite3
import time
from typing import Optional, Tuple

class SQLiteRateLimiter:
    """Rate limiter implementation using SQLite."""

    def __init__(self, db_path: str = "ratelimit.db", cache_prefix: str = "ratelimit"):
        """Initialize the SQLite rate limiter.
        
        Args:
            db_path: Path to the SQLite database file.
            cache_prefix: Prefix for rate limit keys.
        """
        self.db_path = db_path
        self.cache_prefix = cache_prefix
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS rate_limits (
                    key TEXT PRIMARY KEY,
                    count INTEGER NOT NULL,
                    window_start INTEGER NOT NULL
                )
            """)
            conn.execute("CREATE INDEX IF NOT EXISTS idx_window ON rate_limits(window_start)")
            conn.commit()

    def _get_window_key(self, key: str, window: str) -> str:
        """Generate a unique key for the rate limit window."""
        return f"{self.cache_prefix}:{key}:{window}"

    def check_rate_limit(
        self, key: str, max_requests: int, window: str
    ) -> Tuple[bool, dict]:
        """Check if the rate limit has been exceeded.

        Args:
            key: The rate limit key.
            max_requests: Maximum number of requests allowed in the window.
            window: Time window in seconds.

        Returns:
            Tuple containing:
                - Boolean indicating if the limit was exceeded
                - Dict with rate limit information
        """
        window_key = self._get_window_key(key, window)
        current_time = int(time.time())
        window_start = current_time - int(window)

        with sqlite3.connect(self.db_path) as conn:
            # Clean up old entries
            conn.execute("DELETE FROM rate_limits WHERE window_start < ?", (window_start,))
            
            # Get current count
            cursor = conn.execute(
                "SELECT count FROM rate_limits WHERE key = ?", (window_key,)
            )
            row = cursor.fetchone()
            current_count = row[0] if row else 0

            remaining = max_requests - current_count
            is_allowed = remaining > 0

            info = {
                "limit": max_requests,
                "remaining": remaining,
                "reset": window_start + int(window),
            }

            return is_allowed, info

    def increment(
        self, key: str, window: str, amount: int = 1
    ) -> Optional[int]:
        """Increment the rate limit counter.

        Args:
            key: The rate limit key.
            window: Time window in seconds.
            amount: Amount to increment by.

        Returns:
            Current count after increment, or None if failed.
        """
        try:
            window_key = self._get_window_key(key, window)
            current_time = int(time.time())

            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    INSERT INTO rate_limits (key, count, window_start)
                    VALUES (?, ?, ?)
                    ON CONFLICT(key) DO UPDATE SET
                        count = count + ?,
                        window_start = ?
                """, (window_key, amount, current_time, amount, current_time))
                conn.commit()

                cursor = conn.execute(
                    "SELECT count FROM rate_limits WHERE key = ?",
                    (window_key,)
                )
                row = cursor.fetchone()
                return row[0] if row else None
        except Exception:
            return None