import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from starlette.exceptions import HTTPException as StarletteHTTPException
from strawberry.fastapi import GraphQLRouter

# Internal imports
from app.config import settings
from app.database import connect_to_mongo, close_mongo_connection, check_database_health
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
    logger.info("Starting User Service...")
    try:
        await connect_to_mongo()
        logger.info("Database connected successfully")
    except Exception as e:
        logger.error(f"Failed to connect to database: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down User Service...")
    await close_mongo_connection()
    logger.info("Database connection closed")


# Create FastAPI app
app = FastAPI(
    title="User Service",
    description="User management service for fullstack Web3 DApp",
    version="1.0.0",
    debug=settings.debug,
    lifespan=lifespan
)

# Add middleware
app.add_middleware(LoggingMiddleware)
app.add_middleware(CORSMiddleware, allowed_origins=settings.allowed_origins)

# Add exception handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Create GraphQL router
graphql_app = GraphQLRouter(
    schema, 
    graphiql=settings.debug  # Enable GraphiQL in debug mode
)

# Include GraphQL router
app.include_router(graphql_app, prefix="/graphql")

# Health check endpoint
@app.get("/health")
async def health():
    """Health check endpoint"""
    db_healthy = await check_database_health()
    
    return {
        "status": "OK" if db_healthy else "ERROR",
        "service": "user-service",
        "version": "1.0.0",
        "database": "connected" if db_healthy else "disconnected"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "user-service",
        "version": "1.0.0",
        "graphql_endpoint": "/graphql",
        "health_endpoint": "/health"
    }
