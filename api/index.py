# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.routers import ml

# Initialize FastAPI app
app = FastAPI(
    title="StatCorr ML Engine",
    description="Microservice untuk kalkulasi statistik & machine learning",
    version="3.0.0"
)

# CORS Configuration untuk Vercel
origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.get("/")
def read_root():
    return {
        "status": "Online",
        "service": "StatCorr ML Engine",
        "version": "3.0.0",
        "endpoint": "/analyze/correlation-upload"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "StatCorr ML Engine"
    }

# Include ML router
app.include_router(ml.router)

# Mangum handler untuk Vercel
handler = Mangum(app, lifespan="off")