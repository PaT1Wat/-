from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from sqlalchemy.exc import IntegrityError


class ErrorHandlerMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except HTTPException:
            raise
        except IntegrityError as e:
            error_code = getattr(e.orig, "pgcode", None) if e.orig else None
            if error_code == "23505":  # unique_violation
                return JSONResponse(
                    status_code=409,
                    content={"detail": "Resource already exists"}
                )
            elif error_code == "23503":  # foreign_key_violation
                return JSONResponse(
                    status_code=400,
                    content={"detail": "Referenced resource not found"}
                )
            return JSONResponse(
                status_code=500,
                content={"detail": "Database error"}
            )
        except Exception as e:
            return JSONResponse(
                status_code=500,
                content={"detail": str(e) if request.app.state.environment == "development" else "Internal server error"}
            )
