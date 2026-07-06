from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

app = FastAPI(
    title="ReconHive",
    description="Enterprise Security Assessment Management Platform",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    return {"status": "healthy", "version": "2.0.0"}

@app.get("/")
def root():
    return {
        "name": "ReconHive",
        "version": "2.0.0",
        "modules": [
            "Asset Inventory",
            "Target Management",
            "Scan Management",
            "Job Queue",
            "Plugin Framework",
            "Evidence Management",
            "Dashboard",
            "Global Search"
        ]
    }
