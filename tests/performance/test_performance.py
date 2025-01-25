"""Performance test suite for email validation service."""
import asyncio
import time
import statistics
from typing import List
import pytest
from locust import HttpUser, task, between
from concurrent.futures import ThreadPoolExecutor

from app.utils.validation_orchestrator import validate_email, validate_emails_batch
from app.utils.smtp_verifier import verify_smtp
from app.utils.dns_resolver import validate_dns
from app.utils.metrics import ValidationTimer
from ..conftest import VALID_TEST_EMAILS, INVALID_TEST_EMAILS

# Performance SLAs
MAX_SINGLE_VALIDATION_TIME = 2.0  # seconds
MAX_BATCH_VALIDATION_TIME = 5.0  # seconds
MIN_BATCH_THROUGHPUT = 10  # validations/second
MAX_API_RESPONSE_TIME = 0.5  # seconds
MIN_CACHE_HIT_RATIO = 0.95  # 95% cache hit rate

async def measure_validation_time(email: str) -> float:
    """Measure time taken for single email validation."""
    start = time.time()
    await validate_email(email)
    return time.time() - start

async def measure_batch_validation_time(emails: List[str]) -> float:
    """Measure time taken for batch validation."""
    start = time.time()
    await validate_emails_batch(emails)
    return time.time() - start

def test_single_validation_performance():
    """Test single email validation performance."""
    email = VALID_TEST_EMAILS[0]
    
    # Run multiple iterations
    times = []
    for _ in range(10):
        with ValidationTimer() as timer:
            result = validate_email(email)
            times.append(timer.duration)
            
        assert result["valid"]
    
    avg_time = statistics.mean(times)
    p95_time = statistics.quantiles(times, n=20)[18]  # 95th percentile
    
    assert avg_time < MAX_SINGLE_VALIDATION_TIME
    assert p95_time < MAX_SINGLE_VALIDATION_TIME * 1.5
    assert max(times) < MAX_SINGLE_VALIDATION_TIME * 2

@pytest.mark.asyncio
async def test_batch_validation_performance():
    """Test batch email validation performance."""
    emails = VALID_TEST_EMAILS * 5  # 15 emails
    
    # Run multiple iterations
    times = []
    for _ in range(5):
        duration = await measure_batch_validation_time(emails)
        times.append(duration)
    
    avg_time = statistics.mean(times)
    throughput = len(emails) / avg_time
    
    assert avg_time < MAX_BATCH_VALIDATION_TIME
    assert throughput > MIN_BATCH_THROUGHPUT

@pytest.mark.asyncio
async def test_concurrent_validation_scaling():
    """Test validation performance under concurrent load."""
    emails = VALID_TEST_EMAILS + INVALID_TEST_EMAILS
    concurrent_validations = 10
    
    start = time.time()
    
    # Run validations concurrently
    tasks = []
    for email in emails * concurrent_validations:
        tasks.append(measure_validation_time(email))
    
    times = await asyncio.gather(*tasks)
    
    total_time = time.time() - start
    total_validations = len(tasks)
    throughput = total_validations / total_time
    
    assert throughput > MIN_BATCH_THROUGHPUT
    assert statistics.mean(times) < MAX_SINGLE_VALIDATION_TIME * 2

def test_component_performance():
    """Test individual component performance."""
    email = VALID_TEST_EMAILS[0]
    iterations = 50
    
    # DNS performance
    dns_times = []
    for _ in range(iterations):
        start = time.time()
        result = validate_dns(email)
        dns_times.append(time.time() - start)
        assert result["valid"]
    
    # SMTP performance
    smtp_times = []
    for _ in range(iterations):
        start = time.time()
        result = verify_smtp(email)
        smtp_times.append(time.time() - start)
        assert result["valid"]
    
    # Component timing assertions
    assert statistics.mean(dns_times) < 0.1  # DNS < 100ms
    assert statistics.mean(smtp_times) < 1.0  # SMTP < 1s

class ValidationLoadTest(HttpUser):
    """Load test for validation API endpoints."""
    
    wait_time = between(0.5, 2)
    
    @task(3)
    def validate_single_email(self):
        """Test single email validation endpoint."""
        email = VALID_TEST_EMAILS[0]
        with self.client.post(
            "/validate/email",
            json={"email": email},
            catch_response=True
        ) as response:
            assert response.status_code == 200
            assert response.elapsed.total_seconds() < MAX_API_RESPONSE_TIME
    
    @task
    def validate_batch_emails(self):
        """Test batch validation endpoint."""
        emails = VALID_TEST_EMAILS[:3]
        with self.client.post(
            "/validate/batch",
            json={"emails": emails},
            catch_response=True
        ) as response:
            assert response.status_code == 200
            assert response.elapsed.total_seconds() < MAX_API_RESPONSE_TIME * 2
    
    @task
    def get_cached_result(self):
        """Test result retrieval endpoint."""
        with self.client.get(
            "/results/test-id",
            catch_response=True
        ) as response:
            if response.status_code == 404:
                # Expected for unknown ID
                response.success()
            else:
                assert response.elapsed.total_seconds() < MAX_API_RESPONSE_TIME / 2