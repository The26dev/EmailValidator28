import unittest
from app.utils.email_validator import EmailValidator
from unittest.mock import patch, MagicMock
from app.utils.error_handler import ValidationFailedError

class TestEmailValidator(unittest.TestCase):
    def setUp(self):
        self.validator = EmailValidator()
        self.test_email = "test@example.com"
        self.invalid_email = "invalid-email"
        self.disposable_email = "test@tempmail.com"

    @patch('app.utils.dns_resolver.resolve_mx_records')
    @patch('app.utils.domain_reputation_checker.check_domain_reputation')
    @patch('app.utils.disposable_email_detector.check_disposable_email')
    def test_validate_email_success(self, mock_disposable, mock_reputation, mock_mx):
        # Setup mocks
        mock_mx.return_value = ["mx.example.com"]
        mock_reputation.return_value = {"score": 80}
        mock_disposable.return_value = False

        # Test validation
        result = self.validator.validate_email(self.test_email)
        
        # Assertions
        self.assertTrue(result["is_valid"])
        self.assertEqual(result["email"], self.test_email)
        self.assertTrue(result["checks"]["has_mx_records"])
        self.assertFalse(result["checks"]["is_disposable"])
        self.assertEqual(len(result["reasons"]), 0)

    def test_validate_email_invalid_syntax(self):
        result = self.validator.validate_email(self.invalid_email)
        self.assertFalse(result["is_valid"])
        self.assertIn("Invalid email syntax", result["reasons"])

    @patch('app.utils.dns_resolver.resolve_mx_records')
    def test_validate_email_no_mx_records(self, mock_mx):
        mock_mx.return_value = []
        result = self.validator.validate_email(self.test_email)
        self.assertFalse(result["is_valid"])
        self.assertIn("No MX records found", result["reasons"])

    @patch('app.utils.dns_resolver.resolve_mx_records')
    @patch('app.utils.domain_reputation_checker.check_domain_reputation')
    @patch('app.utils.disposable_email_detector.check_disposable_email')
    def test_validate_email_disposable(self, mock_disposable, mock_reputation, mock_mx):
        mock_mx.return_value = ["mx.tempmail.com"]
        mock_reputation.return_value = {"score": 50}
        mock_disposable.return_value = True

        result = self.validator.validate_email(self.disposable_email)
        self.assertFalse(result["is_valid"])
        self.assertTrue(result["checks"]["is_disposable"])
        self.assertIn("Disposable email service detected", result["reasons"])

    @patch('app.utils.dns_resolver.resolve_mx_records')
    @patch('app.utils.domain_reputation_checker.check_domain_reputation')
    @patch('app.utils.disposable_email_detector.check_disposable_email')
    def test_validate_email_poor_reputation(self, mock_disposable, mock_reputation, mock_mx):
        mock_mx.return_value = ["mx.example.com"]
        mock_reputation.return_value = {"score": 20}
        mock_disposable.return_value = False

        result = self.validator.validate_email(self.test_email)
        self.assertFalse(result["is_valid"])
        self.assertIn("Poor domain reputation", result["reasons"])

    def test_validate_bulk_emails(self):
        emails = [self.test_email, self.invalid_email, self.disposable_email]
        with patch.object(self.validator, 'validate_email') as mock_validate:
            mock_validate.side_effect = [
                {"is_valid": True, "email": self.test_email},
                {"is_valid": False, "email": self.invalid_email},
                {"is_valid": False, "email": self.disposable_email}
            ]
            results = self.validator.validate_bulk(emails)
            
            self.assertEqual(len(results), 3)
            self.assertTrue(results[0]["is_valid"])
            self.assertFalse(results[1]["is_valid"])
            self.assertFalse(results[2]["is_valid"])

    def test_validate_email_exception_handling(self):
        with patch('app.utils.dns_resolver.resolve_mx_records', side_effect=Exception("DNS error")):
            with self.assertRaises(ValidationFailedError) as context:
                self.validator.validate_email(self.test_email)
            self.assertIn("Email validation failed", str(context.exception))

if __name__ == '__main__':
    unittest.main()