import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from strawberry.fastapi import GraphQLRouter

# Internal imports
from app.config import settings
from app.database import connect_to_redis, close_redis_connection, check_redis_health
from app.graphql import schema
from app.middleware import (
    LoggingMiddleware,
    CORSMiddleware, 
    http_exception_handler,
    general_exception_handler
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting Auth Service...")
    try:
        await connect_to_redis()
        logger.info("Redis connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Auth Service...")
    await close_redis_connection()
    logger.info("Redis connection closed")


# Create FastAPI app
app = FastAPI(
    title="Auth Service",
    description="Authentication service for fullstack Web3 DApp",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware, allowed_origins=settings.allowed_origins)
# Note: AuthenticationMiddleware not added globally since GraphQL handles auth per resolver

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema,
    graphiql=settings.debug,  # Enable GraphiQL in debug mode
    context_getter=lambda request: {"request": request}  # Pass request to resolvers
)

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_healthy = await check_redis_health()
    
    return {
        "status": "OK" if redis_healthy else "ERROR",
        "service": "auth-service", 
        "version": "1.0.0",
        "redis": "connected" if redis_healthy else "disconnected"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "auth-service",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
        "health_endpoint": "/health",
        "description": "Authentication service with JWT tokens and user-service integration"
    }
