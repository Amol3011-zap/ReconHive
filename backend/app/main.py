from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router
from app.routes.workflow import router as workflow_router
from app.ai.routers.copilot import router as ai_router
from app.workers.routes import router as workers_router
from app.config import settings
from app.utils.middleware import RequestIdMiddleware
import os

app = FastAPI(
    title="ReconHive",
    description="Enterprise Security Assessment Management Platform",
    version="4.0.0",
)

app.add_middleware(RequestIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)

app.include_router(api_router)
app.include_router(workflow_router)
app.include_router(ai_router)
app.include_router(workers_router)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "3.0.0", "phase": 3}

@app.get("/")
def root():
    return {
        "name": "ReconHive",
        "version": "3.0.0",
        "phase": 3,
        "modules": [
            "Asset Inventory",
            "Target Management",
            "Scan Management",
            "Job Queue",
            "Plugin Framework",
            "Evidence Management",
            "Dashboard",
            "Global Search"
        ],
        "endpoints": "See /docs for OpenAPI documentation",
        "status": "Production Ready"
    }
