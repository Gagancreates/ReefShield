"""
FastAPI application entry point for reef temperature monitoring system.
"""
import logging
import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

try:
    from .routers import temperature
    from .config.locations import REEF_LOCATIONS
except ImportError:
    # Fallback for direct execution
    import sys
    sys.path.append(os.path.dirname(__file__))
    from routers import temperature
    from config.locations import REEF_LOCATIONS

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


# Create FastAPI application
app = FastAPI(
    title="Reef Temperature Monitoring API",
    description="API for coral reef temperature monitoring and bleaching prediction in the Andaman Islands",
    version="1.0.0"
)

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logger.info("Starting Reef Temperature Monitoring API")
    logger.info(f"Configured {len(REEF_LOCATIONS)} reef locations")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logger.info("Shutting down Reef Temperature Monitoring API")

# Configure CORS - must be added before other middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://127.0.0.1:3000").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include routers
app.include_router(temperature.router)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Reef Temperature Monitoring API",
        "version": "1.0.0",
        "status": "operational",
        "locations": len(REEF_LOCATIONS),
        "endpoints": {
            "temperature_analysis": "/api/temperature/analysis",
            "current_data": "/api/temperature/current",
            "locations": "/api/temperature/locations",
            "health": "/api/temperature/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """General health check endpoint."""
    return {
        "status": "healthy",
        "service": "reef-temperature-api",
        "version": "1.0.0"
    }


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "details": str(exc) if os.getenv("DEBUG", "False").lower() == "true" else None
        }
    )


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))
    
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=os.getenv("DEBUG", "False").lower() == "true"
    )