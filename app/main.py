from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import ml
import os

# --- SETUP APLIKASI ---
app = FastAPI(
    title="StatCorr ML Engine",
    description="Microservice khusus untuk kalkulasi statistik & machine learning",
    version="3.0.0"
)

# --- KONFIGURASI CORS ---
# Agar bisa diakses dari frontend mana saja
origins = ["*"] 

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROUTER ---
@app.get("/")
def read_root():
    return {
        "status": "Online",
        "service": "StatCorr ML Engine",
        "message": "Send POST request to /analyze/correlation with file_url"
    }

# Kita hanya pasang satu router: ML
app.include_router(ml.router)