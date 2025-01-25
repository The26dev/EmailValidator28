"""FastAPI application entry point."""
from fastapi import FastAPI
from app.core_application import create_app
from app.middleware.error_handler import setup_error_handlers
from app.middleware.security import setup_security, setup_cors
from app.middleware.request_validator import RequestValidationMiddleware

# Create FastAPI application
app = create_app()

# Configure security features
setup_security(app)
setup_cors(
    app,
    allowed_origins=["http://localhost:3000"],  # Add your frontend origins
    allowed_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allowed_headers=["*"],
    allow_credentials=True
)

# Setup request validation middleware
app.add_middleware(RequestValidationMiddleware)

# Setup error handlers
setup_error_handlers(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)