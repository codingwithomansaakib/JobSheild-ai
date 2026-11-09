from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.routes.health import router as health_router
from app.api.routes.analysis import router as analysis_router


# ============================================================
# JobShield AI - FastAPI Application
# ============================================================

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    description=(
        "Evidence-based AI assistant for analyzing "
        "job and internship opportunities."
    ),
)


# ============================================================
# CORS CONFIGURATION
# Allows React frontend to communicate with FastAPI backend
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# API ROUTES
# ============================================================

# Health check
# GET /api/v1/health
app.include_router(
    health_router,
    prefix="/api/v1",
)


# Job analysis
#
# POST /api/v1/analyses
# POST /api/v1/analyses/{analysis_id}/files
# POST /api/v1/analyses/{analysis_id}/run
# GET  /api/v1/analyses/{analysis_id}
# GET  /api/v1/analyses/{analysis_id}/report
app.include_router(
    analysis_router,
    prefix="/api/v1",
)


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "JobShield AI",
        "version": "0.1.0",
        "message": "JobShield AI API is running.",
        "docs": "/docs",
        "health": "/api/v1/health",
    }
