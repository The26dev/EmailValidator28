"""Tests for results handling functionality."""
import json
import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from app.utils.results_handler import ResultsHandler

@pytest.fixture
def mock_db():
    """Create mock database client."""
    return Mock()

@pytest.fixture
def mock_cache():
    """Create mock cache."""
    return Mock()

@pytest.fixture
def handler(mock_db, mock_cache):
    """Create results handler with mocked dependencies."""
    with patch("app.utils.results_handler.get_db_client", return_value=mock_db), \
         patch("app.utils.results_handler.cache", mock_cache):
        handler = ResultsHandler()
        yield handler

def test_store_result(handler, mock_db, mock_cache):
    """Test storing validation result."""
    result = {
        "email": "test@example.com",
        "valid": True
    }
    user_id = "test-user"
    
    validation_id = handler.store_result(result, user_id)
    
    assert validation_id
    assert mock_cache.set.called
    assert mock_db.insert_validation_result.called
    
    stored = mock_db.insert_validation_result.call_args[0][0]
    assert stored["id"] == validation_id
    assert stored["user_id"] == user_id
    assert "created_at" in stored

def test_get_result_from_cache(handler, mock_cache):
    """Test getting result from cache."""
    cached_result = {
        "id": "test-id",
        "email": "test@example.com"
    }
    mock_cache.get.return_value = json.dumps(cached_result)
    
    result = handler.get_result("test-id")
    
    assert result == cached_result
    assert mock_cache.get.called

def test_get_result_from_db(handler, mock_db, mock_cache):
    """Test getting result from database when not in cache."""
    mock_cache.get.return_value = None
    db_result = {
        "id": "test-id",
        "email": "test@example.com"
    }
    mock_db.get_validation_result.return_value = db_result
    
    result = handler.get_result("test-id")
    
    assert result == db_result
    assert mock_cache.get.called
    assert mock_db.get_validation_result.called
    assert mock_cache.set.called  # Should update cache

def test_get_user_results(handler, mock_db):
    """Test getting results for a user."""
    mock_db.get_user_validation_results.return_value = [
        {"id": "1", "email": "test1@example.com"},
        {"id": "2", "email": "test2@example.com"}
    ]
    
    results = handler.get_user_results("test-user", limit=10)
    
    assert len(results) == 2
    assert mock_db.get_user_validation_results.called
    args = mock_db.get_user_validation_results.call_args[1]
    assert args["user_id"] == "test-user"
    assert args["limit"] == 10

def test_cleanup_old_results(handler, mock_db):
    """Test cleaning up old results."""
    mock_db.delete_old_validation_results.return_value = 5
    
    deleted = handler.cleanup_old_results(max_age_days=30)
    
    assert deleted == 5
    assert mock_db.delete_old_validation_results.called
    cutoff = mock_db.delete_old_validation_results.call_args[0][0]
    assert isinstance(cutoff, datetime)
    age = datetime.utcnow() - cutoff
    assert age.days == 30