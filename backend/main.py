"""
ReefShield Backend API
Main FastAPI application entry point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from pathlib import Path
from contextlib import asynccontextmanager

# Import routes and services
from app.api.routes import router
from app.services.model_service import ModelService
from app.services.scheduler_service import SchedulerService
from app.utils.logging_config import setup_logging, get_logger
from config import settings

# Configure advanced logging
setup_logging()
logger = get_logger(__name__)

# Global service instances
model_service: ModelService = None
scheduler_service: SchedulerService = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan context manager"""
    global model_service, scheduler_service
    
    # Startup
    logger.info("ReefShield Backend API starting up...")
    
    try:
        # Initialize services
        model_service = ModelService()
        scheduler_service = SchedulerService(model_service)
        
        # Start the scheduler
        await scheduler_service.start()
        
        # Verify models directory exists
        models_path = settings.MODELS_DIR
        if models_path.exists():
            logger.info(f"Models directory found: {models_path}")
        else:
            logger.warning(f"Models directory not found: {models_path}")
        
        logger.info("ReefShield Backend API startup complete")
        
        yield
        
    finally:
        # Shutdown
        logger.info("ReefShield Backend API shutting down...")
        
        if scheduler_service:
            await scheduler_service.stop()
        
        logger.info("ReefShield Backend API shutdown complete")

# Create FastAPI app instance with lifespan
app = FastAPI(
    title="ReefShield API",
    description="API for coral reef temperature monitoring and prediction",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS for frontend integration
if settings.ENVIRONMENT == "development":
    # Development CORS - Allow localhost origins
    cors_origins = [
        "http://localhost:3000",  # Next.js default dev server
        "http://127.0.0.1:3000",
        "http://localhost:3001",  # Alternative port
        "http://localhost:8080",  # Additional dev port
    ]
else:
    # Production CORS - Restrict to specific domains
    cors_origins = [
        "https://reefshield.app",  # Production domain
        "https://www.reefshield.app",
        # Add other production domains as needed
    ]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=[
        "Accept",
        "Accept-Language",
        "Content-Language",
        "Content-Type",
        "Authorization",
        "X-Requested-With",
    ],
    expose_headers=["X-Total-Count", "X-Rate-Limit-Remaining"],
)

# Basic health check endpoint
@app.get("/")
async def root():
    """Root endpoint with basic API information"""
    return {
        "message": "ReefShield API is running",
        "version": "1.0.0",
        "status": "active"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "ReefShield Backend",
        "version": "1.0.0"
    }

# Include API routes (will be uncommented in Phase 3)
app.include_router(router)

# Service accessor functions for dependency injection
def get_model_service() -> ModelService:
    """Get the model service instance"""
    global model_service
    if model_service is None:
        model_service = ModelService()
    return model_service

def get_scheduler_service() -> SchedulerService:
    """Get the scheduler service instance"""
    global scheduler_service
    if scheduler_service is None:
        scheduler_service = SchedulerService(get_model_service())
    return scheduler_service

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,  # Enable hot reload for development
        log_level="info"
    )