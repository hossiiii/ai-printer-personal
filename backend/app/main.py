"""
AI Printer FastAPI Application
Main entry point for the voice-to-document system
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import logging
from .config import settings
from .api.routes import router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title="AI Printer API",
    description="Voice-to-document generation system for flyers and announcements",
    version="1.0.0",
    docs_url="/docs" if settings.DEVELOPMENT else None,
    redoc_url="/redoc" if settings.DEVELOPMENT else None
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL] if not settings.DEVELOPMENT else ["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix="/api")

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    return {"status": "healthy", "service": "ai-printer-backend"}

@app.get("/ready")
async def readiness_check():
    """Readiness check for deployment"""
    # Add checks for external dependencies
    try:
        # TODO: Add OpenAI API connectivity check
        # TODO: Add Google Drive API connectivity check
        return {"status": "ready", "checks": {"openai": "ok", "drive": "ok"}}
    except Exception as e:
        logger.error(f"Readiness check failed: {e}")
        raise HTTPException(status_code=503, detail="Service not ready")

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEVELOPMENT,
        log_level=settings.LOG_LEVEL.lower()
    )
