"""Authentication configuration and dependencies."""
import os
from datetime import datetime, timedelta
from functools import wraps
from typing import Dict, List, Optional, Union

import jwt
from dotenv import load_dotenv
from flask import abort, current_app, g, request
from werkzeug.local import LocalProxy

# Load environment variables
load_dotenv()

# JWT Configuration
JWT_SECRET = os.getenv('JWT_SECRET')
JWT_ALGORITHM = os.getenv('JWT_ALGORITHM', 'HS256')
JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv('JWT_ACCESS_TOKEN_EXPIRE_MINUTES', 30))
JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv('JWT_REFRESH_TOKEN_EXPIRE_DAYS', 7))

# Cookie Configuration
COOKIE_SECURE = True  # Requires HTTPS
COOKIE_SAMESITE = 'Strict'
COOKIE_HTTPONLY = True

# JWT Claims Configuration
REQUIRED_CLAIMS = ['exp', 'token_type']

class AuthenticationError(Exception):
    """Custom exception for authentication errors."""
    pass

class AuthorizationError(Exception):
    """Custom exception for authorization errors."""
    pass