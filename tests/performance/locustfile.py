"""Locust load testing configuration."""
from locust import HttpUser, task, between
from tests.conftest import VALID_TEST_EMAILS

class EmailValidationUser(HttpUser):
    """Simulated user for load testing."""
    
    wait_time = between(1, 3)
    
    def on_start(self):
        """Set up test user."""
        self.api_key = "test-api-key"
        self.headers = {"X-API-Key": self.api_key}
    
    @task(5)
    def validate_single_email(self):
        """Test single email validation."""
        self.client.post(
            "/validate/email",
            json={"email": VALID_TEST_EMAILS[0]},
            headers=self.headers
        )
    
    @task(2)
    def validate_batch_emails(self):
        """Test batch email validation."""
        self.client.post(
            "/validate/batch",
            json={"emails": VALID_TEST_EMAILS[:3]},
            headers=self.headers
        )
    
    @task(3)
    def get_validation_result(self):
        """Test retrieving validation results."""
        self.client.get(
            f"/results/test-id",
            headers=self.headers
        )