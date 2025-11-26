# api/index.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import sys
import os
import traceback

# Debug: Print working directory
print(f"Working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.routers import ml
    print("✓ Successfully imported app.routers.ml")
except ImportError as e:
    print(f"✗ Failed to import app.routers.ml: {e}")
    traceback.print_exc()
    raise

# Initialize FastAPI app
app = FastAPI(
    title="StatCorr ML Engine",
    description="Microservice untuk kalkulasi statistik & machine learning",
    version="3.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
        "version": "3.0.0"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Include router
app.include_router(ml.router, prefix="/ml")

# Handler untuk Vercel
handler = Mangum(app, lifespan="off")