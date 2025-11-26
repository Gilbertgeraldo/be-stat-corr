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
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response
from mangum import Mangum
import traceback

# Debug: Print paths
print(f"[DEBUG] Working directory: {os.getcwd()}")
print(f"[DEBUG] Script directory: {os.path.dirname(os.path.abspath(__file__))}")
print(f"[DEBUG] Python path: {sys.path}")

# Add app directory to path - PENTING untuk Vercel
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)
    print(f"[DEBUG] Added to sys.path: {base_dir}")

# Try import dengan error handling
ml = None
try:
    from app.routers import ml
    print("[SUCCESS] Imported app.routers.ml successfully")
except ImportError as e:
    print(f"[ERROR] Import failed: {e}")
    print(f"[ERROR] Traceback:")
    traceback.print_exc()
    # Jangan raise, biar app tetap bisa start
    ml = None

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
        "version": "3.0.0",
        "ml_module": "loaded" if ml else "not_loaded"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "ml_module": "loaded" if ml else "not_loaded"
    }

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    """Silent response untuk favicon request"""
    return Response(status_code=204)

# Include router kalau ada
if ml:
    app.include_router(ml.router, prefix="/ml")
    print("[SUCCESS] ML router included")
else:
    print("[WARNING] ML router not included - module import failed")
    
    # Fallback route
    @app.get("/ml/analyze/correlation-info")
    def correlation_info_fallback():
        return {
            "error": "ML module not available",
            "status": "module_load_failed"
        }

# Handler untuk Vercel
handler = Mangum(app, lifespan="off")