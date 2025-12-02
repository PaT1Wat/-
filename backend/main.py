import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.database import database
from app.config.firebase import initialize_firebase
from app.routers import (
    auth,
    authors,
    books,
    favorites,
    publishers,
    recommendations,
    reviews,
)
from app.middleware.error_handler import http_exception_handler

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    initialize_firebase()
    await database.connect()
    yield
    # Shutdown
    await database.disconnect()


app = FastAPI(
    title="Manga/Novel Recommendation API",
    description="API for discovering, reviewing, and getting personalized recommendations for manga, novels, light novels, manhwa, and manhua.",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGIN", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Exception handler
app.add_exception_handler(Exception, http_exception_handler)


# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": __import__("datetime").datetime.utcnow().isoformat()}


# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(books.router, prefix="/api/books", tags=["Books"])
app.include_router(authors.router, prefix="/api/authors", tags=["Authors"])
app.include_router(publishers.router, prefix="/api/publishers", tags=["Publishers"])
app.include_router(reviews.router, prefix="/api/reviews", tags=["Reviews"])
app.include_router(favorites.router, prefix="/api/favorites", tags=["Favorites"])
app.include_router(recommendations.router, prefix="/api/recommendations", tags=["Recommendations"])


# 404 handler
@app.api_route("/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def catch_all(request: Request, path: str):
    return JSONResponse(status_code=404, content={"error": "Route not found"})


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 3001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
