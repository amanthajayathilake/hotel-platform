from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import (
    auth_router,
    hotels_router,
    room_types_router,
    rate_adjustments_router
)

# Create FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="A comprehensive hotel management system with JWT authentication, "
                "hotel and room management, rate adjustments, and image uploads.",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Health check endpoint
@app.get("/", tags=["Health"])
def health_check():
    """
    Basic health check endpoint.
    Returns application status and version.
    """
    return {
        "status": "healthy",
        "app": settings.PROJECT_NAME,
        "version": settings.VERSION
    }


# Register API routers with /api/v1 prefix
API_V1_PREFIX = "/api/v1"

app.include_router(auth_router, prefix=API_V1_PREFIX)
app.include_router(hotels_router, prefix=API_V1_PREFIX)
app.include_router(room_types_router, prefix=API_V1_PREFIX)
app.include_router(rate_adjustments_router, prefix=API_V1_PREFIX)


# Global exception handler for better error responses
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """
    Catch-all exception handler for unexpected errors.
    In production, you might want to log these to a monitoring service.
    """
    if settings.DEBUG:
        # In debug mode, show detailed error
        return {
            "detail": str(exc),
            "type": type(exc).__name__
        }
    else:
        # In production, hide error details
        return {
            "detail": "An internal error occurred"
        }


if __name__ == "__main__":
    import uvicorn
    
    # Run the application
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG  # Auto-reload in debug mode
    )
