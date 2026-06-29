"""Error handling middleware and custom exception classes."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import logging

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details


class AuthenticationError(Exception):
    """Raised when authentication fails."""

    def __init__(self, message: str = "Authentication failed"):
        self.message = message


class AuthorizationError(Exception):
    """Raised when user lacks required permissions."""

    def __init__(self, message: str = "Insufficient permissions"):
        self.message = message


class BusinessLogicError(Exception):
    """Raised when business logic validation fails."""

    def __init__(self, message: str):
        self.message = message


def setup_error_handlers(app: FastAPI):
    """Register exception handlers with the FastAPI application."""
    @app.exception_handler(ValidationError)
    async def validation_error_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "success": False,
                "error": "validation_error",
                "message": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "details": exc.details,
            },
        )

    @app.exception_handler(AuthenticationError)
    async def auth_error_handler(request: Request, exc: AuthenticationError):
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "success": False,
                "error": "authentication_error",
                "message": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(AuthorizationError)
    async def authz_error_handler(request: Request, exc: AuthorizationError):
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={
                "success": False,
                "error": "authorization_error",
                "message": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(BusinessLogicError)
    async def business_logic_error_handler(request: Request, exc: BusinessLogicError):
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={
                "success": False,
                "error": "business_logic_error",
                "message": exc.message,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "success": False,
                "error": "internal_server_error",
                "message": "An unexpected error occurred",
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
        )
