"""
Bens Workout Web App - FastAPI Application

it is a web app about fitness. It will have a sign in for users, account, video tutorials, users can also track their progress, meals, calories, metrics. There will also be a leaderboard of all users.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes import health

app = FastAPI(
    title="Bens Workout Web App",
    description="it is a web app about fitness. It will have a sign in for users, account, video tutorials, users can also track their progress, meals, calories, metrics. There will also be a leaderboard of all users.",
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
        "message": "Welcome to Bens Workout Web App API",
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
