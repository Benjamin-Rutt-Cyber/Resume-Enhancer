"""
Enhanced Test SaaS - FastAPI Application

A complete SaaS application with authentication, payments, and real-time features for task management
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health

app = FastAPI(
    title="Enhanced Test SaaS",
    description="A complete SaaS application with authentication, payments, and real-time features for task management",
    version="0.1.0",
)

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


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Enhanced Test SaaS API",
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
