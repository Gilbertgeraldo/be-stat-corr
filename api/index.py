# api/index.py
import sys
import os

# Fix: Set UTF-8 encoding untuk Windows
if sys.platform == "win32":
    os.environ["PYTHONIOENCODING"] = "utf-8"
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from fastapi import FastAPI

from fastapi.responses import Response
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum
import traceback

# Debug: Print working directory
print(f"Working directory: {os.getcwd()}")
print(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")

# Add app directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from app.routers import ml
    print("[OK] Successfully imported app.routers.ml")
except ImportError as e:
    print(f"[ERROR] Failed to import app.routers.ml: {e}")
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
@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Silent response untuk favicon request"""
    return Response(status_code=204)

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