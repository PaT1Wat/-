from datetime import datetime, timezone
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.settings import settings
from app.config.firebase import initialize_firebase
from app.config.supabase_auth import is_supabase_auth_configured
from app.routers import (
    auth_router,
    books_router,
    authors_router,
    publishers_router,
    reviews_router,
    favorites_router,
    recommendations_router,
)
from app.schemas import HealthResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    if is_supabase_auth_configured():
        print("Supabase Auth is configured and ready")
    else:
        print("Supabase Auth is not configured (will use Firebase or JWT only)")
    app.state.environment = settings.environment
    print(f"Server starting in {settings.environment} mode")
    yield
    # Shutdown
    print("Server shutting down")


app = FastAPI(
    title="Manga/Novel Recommendation API",
    description="API for manga/novel recommendation system with Thai language support",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin.split(",") if settings.cors_origin != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now(timezone.utc)
    )


# Include routers
app.include_router(auth_router, prefix="/api")
app.include_router(books_router, prefix="/api")
app.include_router(authors_router, prefix="/api")
app.include_router(publishers_router, prefix="/api")
app.include_router(reviews_router, prefix="/api")
app.include_router(favorites_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint."""
    return {
        "message": "Manga/Novel Recommendation API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.port,
        reload=settings.environment == "development"
    )
