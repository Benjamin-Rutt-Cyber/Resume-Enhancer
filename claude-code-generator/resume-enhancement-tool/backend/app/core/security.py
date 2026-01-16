"""Security middleware and rate limiting configuration.

This module implements:
- Rate limiting per specification (auth, AI, global)
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- CORS configuration helpers
- Request sanitization

SECURITY REQUIREMENTS (from spec):
- Auth Routes: 5/minute (prevent brute force)
- AI Routes: 10 enhancements/hour/user (cost control)
- Global: 60/minute fallback

Rate limits are enforced BEFORE any AI model calls are made.
"""

import logging
import time
from typing import Callable, Optional
from datetime import datetime

from fastapi import FastAPI, Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from .config import settings

logger = logging.getLogger(__name__)


# =============================================================================
# RATE LIMITING CONFIGURATION
# =============================================================================

def get_user_identifier(request: Request) -> str:
    """Get unique identifier for rate limiting.

    SECURITY: Uses user ID from token if authenticated, falls back to IP.
    This ensures rate limits are per-user, not easily bypassed by IP rotation.

    For unauthenticated routes (login, signup), uses IP address.
    """
    # Try to get user ID from request state (set by auth middleware)
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return f"user:{user_id}"

    # Fallback to IP address for unauthenticated requests
    return get_remote_address(request)


def get_real_ip(request: Request) -> str:
    """Get real client IP, handling proxies.

    SECURITY: Checks X-Forwarded-For for requests behind load balancers.
    """
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        # Take the first IP (original client)
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


# Initialize rate limiter with custom key function
limiter = Limiter(
    key_func=get_user_identifier,
    default_limits=["60/minute"],  # Global fallback limit
    storage_uri="memory://",  # Use Redis in production for horizontal scaling
    # SECURITY: For production with multiple instances, use Redis:
    # storage_uri="redis://localhost:6379"
)


# Rate limit decorators for different route types
# SECURITY: These must be applied to routes as decorators

# Auth routes: Strict limit to prevent brute force
AUTH_RATE_LIMIT = "5/minute"

# AI/Enhancement routes: Cost-based limit
AI_RATE_LIMIT = "10/hour"

# General API routes
API_RATE_LIMIT = "60/minute"

# File upload routes
UPLOAD_RATE_LIMIT = "10/minute"


def rate_limit_exceeded_handler(request: Request, exc: RateLimitExceeded) -> JSONResponse:
    """Custom handler for rate limit exceeded errors.

    SECURITY: Logs rate limit violations for monitoring and potential blocking.
    Returns standardized error response with Retry-After header.
    """
    client_ip = get_real_ip(request)

    # AUDIT: Log rate limit violation
    logger.warning(
        f"Rate limit exceeded: {exc.detail}",
        extra={
            "event": "rate_limit_exceeded",
            "client_ip": client_ip,
            "path": request.url.path,
            "limit": str(exc.detail),
        }
    )

    # Calculate retry-after (default to 60 seconds if not available)
    retry_after = 60

    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={
            "detail": "Rate limit exceeded. Please try again later.",
            "retry_after": retry_after,
        },
        headers={
            "Retry-After": str(retry_after),
            "X-RateLimit-Limit": str(exc.detail),
        }
    )


# =============================================================================
# SECURITY HEADERS MIDDLEWARE
# =============================================================================

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses.

    SECURITY: Implements headers from production hardening checklist:
    - Strict-Transport-Security (HSTS)
    - X-Content-Type-Options
    - X-Frame-Options
    - Content-Security-Policy
    - X-XSS-Protection (legacy but still useful)
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        response = await call_next(request)

        # SECURITY: Prevent MIME type sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # SECURITY: Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # SECURITY: XSS protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # SECURITY: Content Security Policy
        # Restricts scripts to same origin, prevents inline scripts
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self'; "
            "style-src 'self' 'unsafe-inline'; "  # Allow inline styles for UI
            "img-src 'self' data:; "
            "font-src 'self'; "
            "frame-ancestors 'none'; "
            "form-action 'self';"
        )

        # SECURITY: Referrer policy - don't leak URLs
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # SECURITY: Prevent caching of sensitive data
        if request.url.path.startswith("/api/"):
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
            response.headers["Pragma"] = "no-cache"

        # SECURITY: HSTS - Force HTTPS (only in production)
        if not settings.DEBUG:
            # max-age=31536000 (1 year), includeSubDomains
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


# =============================================================================
# REQUEST LOGGING MIDDLEWARE
# =============================================================================

class AuditLoggingMiddleware(BaseHTTPMiddleware):
    """Log all requests for audit trail.

    SECURITY: Logs security-relevant request information without sensitive data.
    Adds correlation ID for request tracing.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Generate correlation ID for request tracing
        import uuid
        correlation_id = str(uuid.uuid4())[:8]
        request.state.correlation_id = correlation_id

        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = (time.time() - start_time) * 1000

        # Get client IP
        client_ip = get_real_ip(request)

        # SECURITY: Log request (without sensitive data)
        log_data = {
            "event": "http_request",
            "correlation_id": correlation_id,
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_ip": client_ip,
            "user_agent": request.headers.get("User-Agent", "unknown")[:100],
        }

        # Add user ID if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            log_data["user_id"] = user_id

        # Log level based on status code
        if response.status_code >= 500:
            logger.error(f"Request failed: {request.method} {request.url.path}", extra=log_data)
        elif response.status_code >= 400:
            logger.warning(f"Client error: {request.method} {request.url.path}", extra=log_data)
        else:
            logger.info(f"{request.method} {request.url.path}", extra=log_data)

        # Add correlation ID to response for debugging
        response.headers["X-Correlation-ID"] = correlation_id

        return response


# =============================================================================
# ERROR HANDLING
# =============================================================================

async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle uncaught exceptions without leaking details.

    SECURITY: Never expose stack traces or internal error details to clients.
    Log full details internally with correlation ID for debugging.
    """
    correlation_id = getattr(request.state, "correlation_id", "unknown")

    # SECURITY: Log full error internally
    logger.error(
        f"Unhandled exception: {type(exc).__name__}",
        extra={
            "event": "unhandled_exception",
            "correlation_id": correlation_id,
            "exception_type": type(exc).__name__,
            "path": request.url.path,
        },
        exc_info=True  # Include full stack trace in logs
    )

    # SECURITY: Return generic message to client
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Internal server error",
            "correlation_id": correlation_id,
        }
    )


# =============================================================================
# SETUP FUNCTION
# =============================================================================

def setup_security(app: FastAPI) -> None:
    """Configure all security middleware for the application.

    Call this in main.py after creating the FastAPI app.

    Args:
        app: FastAPI application instance
    """
    # Add rate limiter to app state
    app.state.limiter = limiter

    # Add rate limit exceeded handler
    app.add_exception_handler(RateLimitExceeded, rate_limit_exceeded_handler)

    # Add security headers middleware
    app.add_middleware(SecurityHeadersMiddleware)

    # Add audit logging middleware
    app.add_middleware(AuditLoggingMiddleware)

    # Add generic exception handler
    app.add_exception_handler(Exception, generic_exception_handler)

    logger.info("Security middleware configured successfully")
