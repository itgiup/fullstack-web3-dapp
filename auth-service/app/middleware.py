import logging
import time
import traceback
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from typing import Optional

from app.services import JWTService
from app.config import settings

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware for logging requests and responses"""
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url}")
        
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(f"Response: {response.status_code} - {process_time:.4f}s")
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(f"Request failed: {request.method} {request.url} - {process_time:.4f}s - {str(e)}")
            logger.error(traceback.format_exc())
            
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "message": "An unexpected error occurred"
                }
            )


class CORSMiddleware(BaseHTTPMiddleware):
    """Custom CORS middleware"""
    
    def __init__(self, app, allowed_origins: list = None):
        super().__init__(app)
        self.allowed_origins = allowed_origins or ["*"]
    
    async def dispatch(self, request: Request, call_next):
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = Response()
            self.add_cors_headers(response, request)
            return response
        
        # Process normal requests
        response = await call_next(request)
        self.add_cors_headers(response, request)
        
        return response
    
    def add_cors_headers(self, response: Response, request: Request):
        origin = request.headers.get("origin")
        
        if origin in self.allowed_origins or "*" in self.allowed_origins:
            response.headers["Access-Control-Allow-Origin"] = origin or "*"
        
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        response.headers["Access-Control-Allow-Credentials"] = "true"


class AuthenticationMiddleware(BaseHTTPMiddleware):
    """JWT Authentication middleware"""
    
    def __init__(self, app):
        super().__init__(app)
        # Paths that don't require authentication
        self.public_paths = {
            "/health",
            "/",
            "/graphql",  # GraphQL handles its own auth per resolver
        }
    
    async def dispatch(self, request: Request, call_next):
        # Skip auth for public paths
        if request.url.path in self.public_paths:
            return await call_next(request)
        
        # Skip auth for GraphQL introspection in debug mode
        if request.url.path == "/graphql" and settings.debug:
            return await call_next(request)
        
        # Get authorization header
        auth_header = request.headers.get("authorization")
        if not auth_header:
            return JSONResponse(
                status_code=401,
                content={"error": "Missing authorization header"}
            )
        
        # Parse token
        try:
            scheme, token = auth_header.split()
            if scheme.lower() != "bearer":
                return JSONResponse(
                    status_code=401,
                    content={"error": "Invalid authorization scheme"}
                )
        except ValueError:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid authorization header format"}
            )
        
        # Verify token
        payload = JWTService.verify_access_token(token)
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"error": "Invalid or expired token"}
            )
        
        # Add user to request context
        request.state.user = payload
        
        # Update user activity
        await JWTService.update_user_activity(payload.user_id)
        
        return await call_next(request)


# Helper function to get current user from request
def get_current_user(request: Request) -> Optional[object]:
    """Get current authenticated user from request"""
    return getattr(request.state, "user", None)


# Exception handlers
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    """Handle HTTP exceptions"""
    logger.warning(f"HTTP Exception: {exc.status_code} - {exc.detail}")
    
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": f"HTTP {exc.status_code}",
            "message": exc.detail
        }
    )


async def general_exception_handler(request: Request, exc: Exception):
    """Handle general exceptions"""
    logger.error(f"Unhandled exception: {str(exc)}")
    logger.error(traceback.format_exc())
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred"
        }
    )
