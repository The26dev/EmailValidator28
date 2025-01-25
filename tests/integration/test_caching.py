"""Integration tests for validation result caching."""
import pytest
import json
from unittest.mock import patch

from app.utils.results_handler import ResultsHandler
from app.utils.cache_manager import cache
from ..conftest import VALID_TEST_EMAILS

@pytest.fixture
def test_result():
    """Create test validation result."""
    return {
        "id": "test-123",
        "email": VALID_TEST_EMAILS[0],
        "valid": True,
        "score": 85.5,
        "checks": {
            "dns": {"valid": True},
            "smtp": {"valid": True}
        }
    }

def test_cache_result_storage(handler, test_result):
    """Test storing result in cache."""
    validation_id = handler.store_result(test_result, "test-user")
    
    # Check cache
    cache_key = f"validation:{validation_id}"
    cached = cache.get(cache_key)
    assert cached
    
    cached_data = json.loads(cached)
    assert cached_data["id"] == validation_id
    assert cached_data["email"] == test_result["email"]
    assert cached_data["user_id"] == "test-user"

def test_cache_result_retrieval(handler, test_result):
    """Test retrieving result from cache."""
    validation_id = handler.store_result(test_result, "test-user")
    
    # Get result - should come from cache
    with patch("app.utils.results_handler.track_cache_hit") as mock_hit:
        result = handler.get_result(validation_id)
        assert mock_hit.called
        
    assert result["id"] == validation_id
    assert result["email"] == test_result["email"]

def test_cache_miss_db_fallback(handler, test_result, mock_db):
    """Test cache miss with database fallback."""
    validation_id = "missing-id"
    db_result = test_result.copy()
    db_result["id"] = validation_id
    mock_db.get_validation_result.return_value = db_result
    
    # Get result - should miss cache and hit DB
    with patch("app.utils.results_handler.track_cache_miss") as mock_miss:
        result = handler.get_result(validation_id)
        assert mock_miss.called
        
    assert result["id"] == validation_id
    assert mock_db.get_validation_result.called
    
    # Result should now be cached
    cache_key = f"validation:{validation_id}"
    assert cache.get(cache_key)

def test_cache_expiry(handler, test_result):
    """Test cache expiry behavior."""
    # Use short TTL
    handler.cache_ttl = 1
    validation_id = handler.store_result(test_result, "test-user")
    
    # Result should be in cache initially
    assert handler.get_result(validation_id)
    
    # Wait for expiry
    import time
    time.sleep(1.5)
    
    # Should miss cache and hit DB
    with patch("app.utils.results_handler.track_cache_miss") as mock_miss:
        handler.get_result(validation_id)
        assert mock_miss.called

def test_cache_invalid_data(handler):
    """Test handling of invalid cached data."""
    # Store invalid JSON in cache
    cache_key = "validation:invalid"
    cache.set(cache_key, "invalid json")
    
    # Should handle gracefully and try DB
    result = handler.get_result("invalid")
    assert not result  # No DB configured in this test

def test_cache_concurrent_access(handler, test_result):
    """Test concurrent cache access."""
    import threading
    
    def store_result():
        handler.store_result(test_result, "test-user")
        
    def get_result(validation_id):
        return handler.get_result(validation_id)
        
    # Start multiple threads
    threads = []
    for _ in range(5):
        t = threading.Thread(target=store_result)
        threads.append(t)
        t.start()
        
    # Wait for all threads
    for t in threads:
        t.join()
        
    # Verify results
    stored = handler.get_result(test_result["id"])
    assert stored
    assert stored["email"] == test_result["email"]