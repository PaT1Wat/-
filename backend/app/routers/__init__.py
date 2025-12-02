from .auth import router as auth_router
from .books import router as books_router
from .authors import router as authors_router
from .publishers import router as publishers_router
from .reviews import router as reviews_router
from .favorites import router as favorites_router
from .recommendations import router as recommendations_router

# Aliased for import in main.py
auth = type('AuthRouter', (), {'router': auth_router})()
books = type('BooksRouter', (), {'router': books_router})()
authors = type('AuthorsRouter', (), {'router': authors_router})()
publishers = type('PublishersRouter', (), {'router': publishers_router})()
reviews = type('ReviewsRouter', (), {'router': reviews_router})()
favorites = type('FavoritesRouter', (), {'router': favorites_router})()
recommendations = type('RecommendationsRouter', (), {'router': recommendations_router})()

__all__ = [
    "auth",
    "books", 
    "authors",
    "publishers",
    "reviews",
    "favorites",
    "recommendations",
]
