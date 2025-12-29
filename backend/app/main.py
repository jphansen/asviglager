"""Main FastAPI application."""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
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
    print("🚀 Starting Asviglager Backend...")
    await MongoDB.connect_db()
    
    # Create indexes
    db = MongoDB.get_db()
    await create_indexes(db)
    
    print(f"✓ Server ready at http://localhost:8000")
    print(f"✓ API docs at http://localhost:8000/docs")
    
    yield
    
    # Shutdown
    print("👋 Shutting down Asviglager Backend...")
    await MongoDB.close_db()


# Create FastAPI app
app = FastAPI(
    title="Asviglager API",
    description="Asset management system backend with product CRUD operations",
    version="0.1.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with API v1 prefix
app.include_router(auth_router, prefix=settings.api_v1_prefix)
app.include_router(products_router, prefix=settings.api_v1_prefix)
app.include_router(warehouses_router, prefix=settings.api_v1_prefix)
app.include_router(photos_router, prefix=settings.api_v1_prefix)


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
