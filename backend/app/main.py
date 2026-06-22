"""Main FastAPI application."""
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.logging import logger
from app.db.mongodb import MongoDB
from app.db.indexes import create_indexes
from app.api.auth import router as auth_router
from app.api.products import router as products_router
from app.api.warehouses import router as warehouses_router
from app.api.photos import router as photos_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for startup and shutdown events."""
    # Startup
    logger.info("Starting Asviglager Backend", fields={"environment": settings.environment})
    await MongoDB.connect_db()
    
    # Create indexes
    db = MongoDB.get_db()
    await create_indexes(db)
    
    logger.info("Server ready", fields={"host": "0.0.0.0", "port": 8000, "docs": "/docs"})
    
    yield
    
    # Shutdown
    logger.info("Shutting down Asviglager Backend")
    logger.flush()
    await MongoDB.close_db()


# Create FastAPI app
app = FastAPI(
    title="Asviglager API",
    description="Asset management system backend with product CRUD operations",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
origins = settings.cors_origins
if "*" in origins:
    # When allowing all origins, we can't use credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
else:
    # Specific origins can use credentials
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers with API v1 prefix
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(warehouses_router, prefix=settings.api_v1_prefix)
app.include_router(photos_router, prefix=settings.api_v1_prefix)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log incoming HTTP requests."""
    start = time.time()
    response = await call_next(request)
    duration_ms = (time.time() - start) * 1000
    logger.info(
        f"{request.method} {request.url.path} {response.status_code}",
        fields={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2),
            "client_host": request.client.host if request.client else None,
        }
    )
    return response


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Asviglager API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    try:
        # Test MongoDB connection
        db = MongoDB.get_db()
        await db.command("ping")
        
        return {
            "status": "healthy",
            "database": "connected",
            "environment": settings.environment
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }
