"""Main FastAPI application"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import tempfile
import json
from typing import List, Optional
import logging

from ..config import get_settings
from .routers import patterns, validation, cmdb, analytics, history
from ..database.session import init_db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

# Create FastAPI app
app = FastAPI(
    title="Architecture Validation & Pattern Management System",
    description="POC system for validating infrastructure against architectural standards",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and other startup tasks"""
    logger.info("Initializing database...")
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        # Continue anyway for POC - database is optional

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(patterns.router, prefix="/api/patterns", tags=["patterns"])
app.include_router(validation.router, prefix="/api/validate", tags=["validation"])
app.include_router(cmdb.router, prefix="/api/cmdb", tags=["cmdb"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(history.router, prefix="/api/history", tags=["history"])

# Serve static files for frontend
static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Architecture Validation & Pattern Management System",
        "version": "0.1.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": "0.1.0"
    }


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "Architecture Validation API",
        "version": "0.2.0",
        "endpoints": {
            "patterns": "/api/patterns",
            "validation": "/api/validate",
            "cmdb": "/api/cmdb",
            "analytics": "/api/analytics",
            "history": "/api/history"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)
