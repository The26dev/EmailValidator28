"""Session management middleware implementation."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from uuid import uuid4

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.config.settings import settings

class SessionStore:
    """In-memory session store (should be replaced with Redis in production)."""
    def __init__(self):
        self._store: Dict[str, Dict[str, Any]] = {}
        self._expiry: Dict[str, datetime] = {}
        
    def create_session(self, user_id: str, data: Dict[str, Any] = None) -> str:
        """Create a new session."""
        session_id = str(uuid4())
        self._store[session_id] = {
            'user_id': user_id,
            'created_at': datetime.utcnow(),
            'data': data or {}
        }
        self._expiry[session_id] = datetime.utcnow() + timedelta(days=settings.SESSION_EXPIRE_DAYS)
        return session_id
        
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data if it exists and hasn't expired."""
        if session_id in self._store:
            if datetime.utcnow() > self._expiry[session_id]:
                self.delete_session(session_id)
                return None
            return self._store[session_id]
        return None
        
    def update_session(self, session_id: str, data: Dict[str, Any]) -> None:
        """Update session data."""
        if session_id in self._store:
            self._store[session_id]['data'].update(data)
            
    def delete_session(self, session_id: str) -> None:
        """Delete a session."""
        self._store.pop(session_id, None)
        self._expiry.pop(session_id, None)

# Global session store instance
session_store = SessionStore()

class SessionMiddleware(BaseHTTPMiddleware):
    """Middleware to handle session management."""
    
    async def dispatch(self, request: Request, call_next):
        session_id = request.cookies.get('session_id')
        
        if session_id:
            session = session_store.get_session(session_id)
            if session:
                request.state.session = session
                request.state.session_id = session_id
            else:
                # Invalid or expired session
                session_id = None
                
        response = await call_next(request)
        
        if hasattr(request.state, 'new_session_id'):
            # Set secure session cookie
            response.set_cookie(
                'session_id',
                request.state.new_session_id,
                max_age=settings.SESSION_EXPIRE_DAYS * 24 * 60 * 60,
                httponly=True,
                secure=True,
                samesite='strict'
            )
            
        return response