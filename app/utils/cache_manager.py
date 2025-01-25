"""
Cache Manager Module
Manages caching mechanisms to optimize performance using SQLite.
"""

import json
import os
from typing import Optional
from app.utils.logger import setup_logger
from .sqlite_cache import SQLiteCacheManager
from ..config.sqlite_config import CACHE_DB_PATH

logger = setup_logger('CacheManager')

class CacheManager(SQLiteCacheManager):
    def __init__(self, host: str = None, port: int = None, db: int = None):
        """
        Initializes the SQLite CacheManager.
        
        Args:
            host (str): Ignored (kept for compatibility)
            port (int): Ignored (kept for compatibility)
            db (int): Ignored (kept for compatibility)
        """
        super().__init__(db_path=CACHE_DB_PATH)
        logger.info("Initialized SQLite Cache Manager")

    def set_cache(self, key: str, value: dict, expire: int = 3600) -> bool:
        """
        Stores data in the cache.
        
        Args:
            key (str): Cache key.
            value (dict): Data to cache.
            expire (int): Expiration time in seconds.
        
        Returns:
            bool: True if successful, False otherwise.
        """
        try:
            result = super().set_cache(key, value, expire)
            if result:
                logger.debug(f"Set cache for key: {key}")
            else:
                logger.error(f"Failed to set cache for key: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to set cache for key {key}: {e}")
            return False

    def get_cache(self, key: str) -> Optional[dict]:
        """
        Retrieves data from the cache.
        
        Args:
            key (str): Cache key.
        
        Returns:
            Optional[dict]: Cached data if available, else None.
        """
        try:
            value = super().get_cache(key)
            if value is not None:
                logger.debug(f"Cache hit for key: {key}")
            else:
                logger.debug(f"Cache miss for key: {key}")
            return value
        except Exception as e:
            logger.error(f"Failed to get cache for key {key}: {e}")
            return None

    def delete_cache(self, key: str) -> bool:
        """
        Deletes a cached key.
        
        Args:
            key (str): Cache key to delete.
        
        Returns:
            bool: True if deletion was successful, False otherwise.
        """
        try:
            result = super().delete_cache(key)
            if result:
                logger.debug(f"Deleted cache for key: {key}")
            else:
                logger.error(f"Failed to delete cache for key: {key}")
            return result
        except Exception as e:
            logger.error(f"Failed to delete cache for key {key}: {e}")
            return False