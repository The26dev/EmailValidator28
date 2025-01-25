from functools import wraps
import logging
import traceback
from flask import jsonify, current_app
from marshmallow import ValidationError

# Set up logging
logging.basicConfig(
    filename='logs/error.log',
    level=logging.ERROR,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class APIError(Exception):
    """Base class for API errors."""
    def __init__(self, message, status_code=400, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv['message'] = self.message
        rv['status'] = 'error'
        return rv

class ValidationFailedError(APIError):
    """Raised when input validation fails."""
    def __init__(self, message="Invalid input", errors=None):
        super().__init__(message, status_code=400)
        self.errors = errors or {}

    def to_dict(self):
        rv = super().to_dict()
        rv['errors'] = self.errors
        return rv

class AuthenticationError(APIError):
    """Raised when authentication fails."""
    def __init__(self, message="Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(APIError):
    """Raised when user doesn't have required permissions."""
    def __init__(self, message="Not authorized"):
        super().__init__(message, status_code=403)

class NotFoundError(APIError):
    """Raised when requested resource is not found."""
    def __init__(self, message="Resource not found"):
        super().__init__(message, status_code=404)

class RateLimitError(APIError):
    """Raised when rate limit is exceeded."""
    def __init__(self, message="Rate limit exceeded"):
        super().__init__(message, status_code=429)

def setup_error_handlers(app):
    """Register error handlers with Flask app."""
    
    @app.errorhandler(APIError)
    def handle_api_error(error):
        response = jsonify(error.to_dict())
        response.status_code = error.status_code
        return response

    @app.errorhandler(ValidationError)
    def handle_validation_error(error):
        return jsonify({
            'status': 'error',
            'message': 'Validation failed',
            'errors': error.messages
        }), 400

    @app.errorhandler(500)
    def handle_server_error(error):
        logger.error(f"Internal Server Error: {str(error)}\n{traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': 'Internal server error'
        }), 500

    @app.errorhandler(404)
    def handle_not_found(error):
        return jsonify({
            'status': 'error',
            'message': 'Resource not found'
        }), 404

def error_logger(f):
    """Decorator to log exceptions."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error in {f.__name__}: {str(e)}\n{traceback.format_exc()}")
            raise
    return decorated_function

def handle_errors(f):
    """Decorator to handle and format errors."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            raise ValidationFailedError(errors=e.messages)
        except Exception as e:
            if not isinstance(e, APIError):
                logger.error(f"Unhandled error in {f.__name__}: {str(e)}\n{traceback.format_exc()}")
                raise APIError("An unexpected error occurred", status_code=500)
            raise
    return decorated_function