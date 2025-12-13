"""
Resume Enhancement Tool - FastAPI Application

A single-user web application for enhancing resumes with AI assistance. Features include job-specific resume tailoring by matching resumes to job descriptions, and comprehensive industry-focused resume revamps for different sectors like IT and cybersecurity. Uses a workspace approach where files are stored locally and Claude Code reads them directly - no API calls. Supports PDF and DOCX input, outputs PDF resumes. Web UI handles organization and viewing, Claude Code performs the enhancement work.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health, resumes, jobs, enhancements

app = FastAPI(
    title="Resume Enhancement Tool",
    description="A single-user web application for enhancing resumes with AI assistance. Features include job-specific resume tailoring by matching resumes to job descriptions, and comprehensive industry-focused resume revamps for different sectors like IT and cybersecurity. Uses a workspace approach where files are stored locally and Claude Code reads them directly - no API calls. Supports PDF and DOCX input, outputs PDF resumes. Web UI handles organization and viewing, Claude Code performs the enhancement work.",
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
app.include_router(resumes.router, prefix="/api", tags=["resumes"])
app.include_router(jobs.router, prefix="/api", tags=["jobs"])
app.include_router(enhancements.router, prefix="/api", tags=["enhancements"])


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
