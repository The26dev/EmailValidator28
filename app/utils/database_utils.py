"""Database utilities for connection pooling and optimization."""
import logging
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

logger = logging.getLogger(__name__)

def create_connection_pool(database_uri: str, min_size: int = 5, max_size: int = 20, 
                         timeout: int = 30):
    """
    Creates and configures a database connection pool.
    
    Args:
        database_uri: Database connection URI
        min_size: Minimum number of connections to keep in the pool
        max_size: Maximum number of connections allowed in the pool
        timeout: Time in seconds to wait for a connection before timing out
        
    Returns:
        SQLAlchemy engine with configured connection pool
    """
    try:
        engine = create_engine(
            database_uri,
            poolclass=QueuePool,
            pool_size=max_size,
            max_overflow=max_size - min_size,
            pool_timeout=timeout,
            pool_pre_ping=True,  # Enable connection health checks
            echo=False
        )
        
        # Test the connection pool
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        
        logger.info(f"Connection pool initialized. Size: {min_size}-{max_size}, Timeout: {timeout}s")
        return engine
        
    except Exception as e:
        logger.error(f"Failed to setup connection pool: {e}")
        raise