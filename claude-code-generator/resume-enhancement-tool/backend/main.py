"""
Resume Enhancement Tool - FastAPI Application

A single-user web application for enhancing resumes with AI assistance. Features include job-specific resume tailoring by matching resumes to job descriptions, and comprehensive industry-focused resume revamps for different sectors like IT and cybersecurity. Uses a workspace approach where files are stored locally and Claude Code reads them directly - no API calls. Supports PDF and DOCX input, outputs PDF resumes. Web UI handles organization and viewing, Claude Code performs the enhancement work.
"""

import logging
import time
from pathlib import Path

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api.routes import health, resumes, jobs, enhancements, style_previews, analysis, comparison

logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)

app = FastAPI(
    title="Resume Enhancement Tool",
    description="A single-user web application for enhancing resumes with AI assistance. Features include job-specific resume tailoring by matching resumes to job descriptions, and comprehensive industry-focused resume revamps for different sectors like IT and cybersecurity. Uses a workspace approach where files are stored locally and Claude Code reads them directly - no API calls. Supports PDF and DOCX input, outputs PDF resumes. Web UI handles organization and viewing, Claude Code performs the enhancement work.",
    version="0.1.0",
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests with timing information."""
    start_time = time.time()

    # Process the request
    response = await call_next(request)

    # Calculate duration
    duration = time.time() - start_time

    # Log request details
    logger.info(
        f"{request.method} {request.url.path} - "
        f"Status: {response.status_code} - "
        f"Duration: {duration:.3f}s"
    )

    return response

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(resumes.router, prefix="/api", tags=["resumes"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(enhancements.router, prefix="/api", tags=["enhancements"])
app.include_router(style_previews.router, prefix="/api", tags=["style-previews"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(comparison.router, prefix="/api", tags=["comparison"])


@app.on_event("startup")
async def validate_config_on_startup():
    """
    Validate production configuration on startup.

    Logs warnings and errors for configuration issues that may affect
    production deployment security and functionality.
    """
    logger.info("Starting Resume Enhancement Tool API...")
    logger.info(f"Version: {settings.APP_VERSION}")
    logger.info(f"Debug mode: {settings.DEBUG}")

    # Validate production configuration
    issues = settings.validate_production_config()

    if issues:
        logger.warning("=" * 80)
        logger.warning("CONFIGURATION ISSUES DETECTED:")
        logger.warning("=" * 80)

        for issue in issues:
            if "CRITICAL" in issue:
                logger.error(f"  ❌ {issue}")
            else:
                logger.warning(f"  ⚠️  {issue}")

        logger.warning("=" * 80)
        logger.warning("Please review your .env configuration before deploying to production!")
        logger.warning("=" * 80)
    else:
        logger.info("✅ Configuration validation passed - production ready")

    # Ensure workspace directory exists
    workspace_path = Path(settings.WORKSPACE_ROOT)
    if not workspace_path.exists():
        logger.info(f"Creating workspace directory: {workspace_path}")
        workspace_path.mkdir(parents=True, exist_ok=True)

    logger.info(f"Workspace directory: {workspace_path.absolute()}")
    logger.info("Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """
    Graceful shutdown handler.

    Performs cleanup operations when the application shuts down:
    - Closes database connections
    - Logs shutdown event for monitoring
    """
    logger.info("Shutting down Resume Enhancement Tool API...")

    # Close database connections
    try:
        from app.core.database import engine
        engine.dispose()
        logger.info("Database connections closed successfully")
    except Exception as e:
        logger.error(f"Error closing database connections: {e}")

    logger.info("Application shutdown complete")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Resume Enhancement Tool API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
