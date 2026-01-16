"""
Resume Enhancement Tool - FastAPI Application

A web application for enhancing resumes with AI assistance. Features include job-specific
resume tailoring by matching resumes to job descriptions, and comprehensive industry-focused
resume revamps for different sectors like IT and cybersecurity.

SECURITY FEATURES:
- JWT authentication with refresh tokens (HttpOnly cookies)
- Token revocation via user_version
- Rate limiting (auth: 5/min, AI: 10/hour, global: 60/min)
- Security headers (HSTS, CSP, X-Frame-Options, etc.)
- RBAC with admin role support
- Audit logging for security events
"""

import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.security import setup_security, limiter
from app.api.routes import health, resumes, jobs, enhancements, style_previews, analysis, comparison, auth
from logging_config import setup_logging

# Initialize structured logging
setup_logging(log_level="INFO" if not settings.DEBUG else "DEBUG")
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Resume Enhancement Tool",
    description=(
        "A web application for enhancing resumes with AI assistance. "
        "Features include job-specific resume tailoring and industry-focused resume revamps."
    ),
    version="0.1.0",
    # SECURITY: Disable docs in production if needed
    # docs_url=None if not settings.DEBUG else "/docs",
    # redoc_url=None if not settings.DEBUG else "/redoc",
)

# SECURITY: Setup rate limiting, security headers, and audit logging
setup_security(app)

# CORS middleware - SECURITY: Credentials enabled for HttpOnly cookie support
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,  # SECURITY: Required for HttpOnly refresh token cookies
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
    expose_headers=["X-Correlation-ID"],  # Allow frontend to access correlation ID
)

# Include routers
app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["authentication"])
app.include_router(resumes.router, prefix="/api", tags=["resumes"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(enhancements.router, prefix="/api", tags=["enhancements"])
app.include_router(style_previews.router, prefix="/api", tags=["style-previews"])
app.include_router(analysis.router, prefix="/api", tags=["analysis"])
app.include_router(comparison.router, prefix="/api", tags=["comparison"])


# Debug router
from fastapi import APIRouter
from pathlib import Path
debug_router = APIRouter()

@debug_router.get("/debug/worker-status")
async def get_worker_status():
    workspace = Path(settings.WORKSPACE_ROOT)
    status = {"status": "unknown"}
    
    # Check heartbeat
    hb_file = workspace / "worker_heartbeat.json"
    if hb_file.exists():
        try:
            import json
            status["heartbeat"] = json.loads(hb_file.read_text())
        except:
            status["heartbeat"] = "corrupt"
    else:
        status["heartbeat"] = "missing"
        
    # Check crash log
    crash_file = workspace / "worker_crash.log"
    if crash_file.exists():
        status["crash_log"] = crash_file.read_text()
        
    # Check stdout/stderr log
    log_file = workspace / "worker.log"
    if log_file.exists():
        status["worker_log"] = log_file.read_text()
        
    return status

app.include_router(debug_router, prefix="/api", tags=["debug"])


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
