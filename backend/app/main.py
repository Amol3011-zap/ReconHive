from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.api import router as api_router
import os

app = FastAPI(
    title="ReconHive",
    description="Enterprise Security Assessment Management Platform",
    version="3.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

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
