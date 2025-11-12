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
from .routers import patterns, validation, cmdb, analytics, history, reports, notifications
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
    version="0.4.0",
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
app.include_router(reports.router, prefix="/api/reports", tags=["reports"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["notifications"])

# Serve static files for frontend
static_path = Path(__file__).parent.parent.parent / "static"
if static_path.exists():
    app.mount("/static", StaticFiles(directory=str(static_path)), name="static")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Architecture Validation & Pattern Management System",
        "version": "0.4.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check():
    """Comprehensive health check endpoint"""
    from ..validation.registry import RuleRegistry
    from ..patterns.library import PatternLibrary
    from ..database.session import get_db
    from datetime import datetime
    import sys

    health_status = {
        "status": "healthy",
        "version": "0.4.0",
        "timestamp": datetime.utcnow().isoformat(),
        "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.patch}",
        "components": {}
    }

    # Check validation rules
    try:
        registry = RuleRegistry()
        rules_count = len(registry.get_all_rules())
        health_status["components"]["validation_engine"] = {
            "status": "healthy",
            "rules_count": rules_count
        }
    except Exception as e:
        health_status["components"]["validation_engine"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check pattern library
    try:
        pattern_lib = PatternLibrary()
        patterns_count = len(pattern_lib.get_all_patterns())
        health_status["components"]["pattern_library"] = {
            "status": "healthy",
            "patterns_count": patterns_count
        }
    except Exception as e:
        health_status["components"]["pattern_library"] = {
            "status": "unhealthy",
            "error": str(e)
        }
        health_status["status"] = "degraded"

    # Check database
    try:
        db = next(get_db())
        db.execute("SELECT 1")
        health_status["components"]["database"] = {
            "status": "healthy",
            "type": "sqlite"
        }
        db.close()
    except Exception as e:
        health_status["components"]["database"] = {
            "status": "degraded",
            "message": "Database not initialized (optional for POC)",
            "error": str(e)
        }
        # Database is optional, so don't mark overall as degraded

    return health_status


@app.get("/api")
async def api_info():
    """API information"""
    return {
        "name": "Architecture Validation API",
        "version": "0.4.0",
        "endpoints": {
            "patterns": "/api/patterns",
            "validation": "/api/validate",
            "cmdb": "/api/cmdb",
            "analytics": "/api/analytics",
            "history": "/api/history",
            "reports": "/api/reports",
            "notifications": "/api/notifications",
            "health": "/health",
            "metrics": "/metrics"
        }
    }


@app.get("/metrics")
async def get_metrics():
    """Get system metrics and statistics"""
    from ..validation.registry import RuleRegistry
    from ..patterns.library import PatternLibrary
    from ..validation.rule import RuleCategory, Severity
    from ..database.session import get_db
    from collections import Counter
    from datetime import datetime
    import os

    metrics = {
        "system": {},
        "validation": {},
        "patterns": {},
        "database": {}
    }

    # System metrics
    try:
        import psutil
        process = psutil.Process(os.getpid())
        metrics["system"] = {
            "memory_usage_mb": round(process.memory_info().rss / 1024 / 1024, 2),
            "cpu_percent": process.cpu_percent(interval=0.1),
            "uptime_seconds": int((datetime.now() - datetime.fromtimestamp(process.create_time())).total_seconds())
        }
    except ImportError:
        metrics["system"] = {"status": "psutil not installed"}
    except Exception as e:
        metrics["system"] = {"status": "unavailable", "error": str(e)}

    # Validation engine metrics
    try:
        registry = RuleRegistry()
        all_rules = registry.get_all_rules()

        categories = Counter([rule.category.value for rule in all_rules])
        severities = Counter([rule.severity.value for rule in all_rules])

        metrics["validation"] = {
            "total_rules": len(all_rules),
            "rules_by_category": dict(categories),
            "rules_by_severity": dict(severities),
            "categories": list(categories.keys())
        }
    except Exception as e:
        metrics["validation"] = {"error": str(e)}

    # Pattern library metrics
    try:
        pattern_lib = PatternLibrary()
        patterns = pattern_lib.get_all_patterns()

        statuses = Counter([p.metadata.status for p in patterns])

        metrics["patterns"] = {
            "total_patterns": len(patterns),
            "patterns_by_status": dict(statuses),
            "pattern_ids": [p.metadata.id for p in patterns]
        }
    except Exception as e:
        metrics["patterns"] = {"error": str(e)}

    # Database metrics
    try:
        from ..database.repository import ValidationHistoryRepository
        db = next(get_db())

        stats = ValidationHistoryRepository.get_compliance_stats(db, days=30)

        metrics["database"] = {
            "validations_last_30_days": stats.get("total_validations", 0),
            "avg_compliance_score": stats.get("avg_compliance_score", 0)
        }

        db.close()
    except Exception as e:
        metrics["database"] = {"status": "not_available", "message": str(e)}

    return metrics


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=settings.app_port)
