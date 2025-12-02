from app.routers.auth import router as auth_router
from app.routers.books import router as books_router
from app.routers.authors import router as authors_router
from app.routers.publishers import router as publishers_router
from app.routers.reviews import router as reviews_router
from app.routers.favorites import router as favorites_router
from app.routers.recommendations import router as recommendations_router

__all__ = [
    "auth_router",
    "books_router",
    "authors_router",
    "publishers_router",
    "reviews_router",
    "favorites_router",
    "recommendations_router",
]
