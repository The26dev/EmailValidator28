"""SQLite-based cache implementation as an alternative to Redis.

This module provides a SQLite-based caching solution that can be used as a drop-in
replacement for Redis in Windows environments. It implements the same interface
as the Redis-based cache manager but uses SQLite for storage.
"""
import json
import sqlite3
import time
from typing import Optional, Dict
from pathlib import Path


class SQLiteCacheManager:
    """Cache manager implementation using SQLite."""

    def __init__(self, db_path: str = "cache.db"):
        """Initialize the SQLite cache manager.
        
        Args:
            db_path: Path to the SQLite database file.
        """
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database with required tables."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    expiry INTEGER NOT NULL
                )
            """)
            # Create index on expiry for faster cleanup
            conn.execute("CREATE INDEX IF NOT EXISTS idx_expiry ON cache(expiry)")
            conn.commit()

    def _cleanup_expired(self):
        """Remove expired cache entries."""
        current_time = int(time.time())
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM cache WHERE expiry < ?", (current_time,))
            conn.commit()

    def set_cache(self, key: str, value: dict, expire: int = 3600) -> bool:
        """Set a value in the cache with an expiration time.

        Args:
            key: The cache key.
            value: The value to cache (must be JSON serializable).
            expire: Time in seconds until the value expires.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            expiry = int(time.time()) + expire
            serialized_value = json.dumps(value)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    "INSERT OR REPLACE INTO cache (key, value, expiry) VALUES (?, ?, ?)",
                    (key, serialized_value, expiry)
                )
                conn.commit()
            return True
        except Exception:
            return False

    def get_cache(self, key: str) -> Optional[dict]:
        """Retrieve a value from the cache.

        Args:
            key: The cache key.

        Returns:
            Optional[dict]: The cached value or None if not found or expired.
        """
        self._cleanup_expired()
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    "SELECT value FROM cache WHERE key = ? AND expiry >= ?",
                    (key, int(time.time()))
                )
                row = cursor.fetchone()
                if row:
                    return json.loads(row[0])
                return None
        except Exception:
            return None

    def delete_cache(self, key: str) -> bool:
        """Delete a value from the cache.

        Args:
            key: The cache key.

        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM cache WHERE key = ?", (key,))
                conn.commit()
            return True
        except Exception:
            return False