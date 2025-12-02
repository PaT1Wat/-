import os
import traceback
from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


async def http_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Global exception handler."""
    
    # Log the error
    print(f"Error: {exc}")
    if os.getenv("NODE_ENV") == "development" or os.getenv("ENVIRONMENT") == "development":
        traceback.print_exc()
    
    # PostgreSQL errors (asyncpg)
    error_message = str(exc)
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    
    # Check for unique constraint violation
    if "unique" in error_message.lower() or "23505" in error_message:
        status_code = status.HTTP_409_CONFLICT
        error_message = "Resource already exists"
    
    # Check for foreign key violation
    elif "foreign key" in error_message.lower() or "23503" in error_message:
        status_code = status.HTTP_400_BAD_REQUEST
        error_message = "Referenced resource not found"
    
    # JWT errors
    elif "token" in error_message.lower():
        if "expired" in error_message.lower():
            status_code = status.HTTP_401_UNAUTHORIZED
            error_message = "Token expired"
        elif "invalid" in error_message.lower():
            status_code = status.HTTP_401_UNAUTHORIZED
            error_message = "Invalid token"
    
    # Build response
    response_content: dict[str, Any] = {"error": error_message}
    
    # Include stack trace in development
    if os.getenv("NODE_ENV") == "development" or os.getenv("ENVIRONMENT") == "development":
        response_content["stack"] = traceback.format_exc()
    
    return JSONResponse(
        status_code=status_code,
        content=response_content,
    )
