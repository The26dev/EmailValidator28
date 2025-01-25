"""SQLite configuration settings."""
import os
from pathlib import Path

# Get the base directory for SQLite databases
BASE_DIR = Path(__file__).parent.parent.parent
DATA_DIR = BASE_DIR / "data"

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# SQLite database paths
CACHE_DB_PATH = str(DATA_DIR / "cache.db")
RATE_LIMIT_DB_PATH = str(DATA_DIR / "ratelimit.db")