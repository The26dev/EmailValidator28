import os
import unittest
from app import create_app
from config.config import Config, DevelopmentConfig, TestingConfig, ProductionConfig

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    def test_config_loading(self):
        self.assertTrue(self.app.config['TESTING'])
        self.assertFalse(self.app.config['DEBUG'])

    def test_development_config(self):
        app = create_app('development')
        self.assertTrue(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])

    def test_production_config(self):
        app = create_app('production')
        self.assertFalse(app.config['DEBUG'])
        self.assertFalse(app.config['TESTING'])

    def test_env_variables_loading(self):
        # Test that environment variables are properly loaded
        os.environ['TEST_DB_USERNAME'] = 'test_user'
        os.environ['TEST_DB_PASSWORD'] = 'test_pass'
        os.environ['TEST_DB_HOST'] = 'localhost'
        os.environ['TEST_DB_PORT'] = '5432'
        os.environ['TEST_DB_NAME'] = 'test_db'

        config = TestingConfig()
        self.assertIn('test_user', config.DATABASE_URI)
        self.assertIn('test_pass', config.DATABASE_URI)
        self.assertIn('localhost', config.DATABASE_URI)
        self.assertIn('5432', config.DATABASE_URI)
        self.assertIn('test_db', config.DATABASE_URI)

    def test_sensitive_data_protection(self):
        # Test that sensitive data is not exposed in config
        config = Config()
        self.assertNotIn('password', str(config.__dict__))
        self.assertNotIn('secret', str(config.__dict__).lower())
        self.assertNotIn('key', str(config.__dict__).lower())

    def test_rate_limiting_config(self):
        # Test rate limiting configuration
        self.assertEqual(self.app.config['RATE_LIMIT_MAX_REQUESTS'], 100)
        self.assertEqual(self.app.config['RATE_LIMIT_WINDOW_SECONDS'], 60)

    def test_logging_config(self):
        # Test logging configuration
        self.assertEqual(self.app.config['LOG_LEVEL'], 'INFO')
        self.assertEqual(self.app.config['LOG_FILE'], 'logs/main.log')
        self.assertEqual(self.app.config['LOG_MAX_BYTES'], 5242880)
        self.assertEqual(self.app.config['LOG_BACKUP_COUNT'], 5)

    def test_redis_config(self):
        # Test Redis/Celery configuration
        config = Config()
        self.assertTrue(config.REDIS_URL.startswith('redis://'))
        self.assertEqual(config.CELERY_BROKER_URL, config.REDIS_URL)
        self.assertEqual(config.CELERY_RESULT_BACKEND, config.REDIS_URL)

if __name__ == '__main__':
    unittest.main()