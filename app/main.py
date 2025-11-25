from fastapi import FastAPI
from app.routers import auth, ml
from fastapi.middleware.cors import CORSMiddleware

# Setup Aplikasi
app = FastAPI(
    title="StatCorr API (Modular)",
    description="Backend Terstruktur dengan Folder",
    version="2.1.0"
)
origins = [
    "http://localhost:3000",           # Untuk testing lokal
    "https://statcorr.vercel.app",     # (Contoh) Domain frontend kamu nanti
    "*"                                # (Opsional) Bolehkan semua domain (untuk development)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root Endpoint
@app.get("/")
def read_root():
    return {"status": "StatCorr API is running modularly!"}

# Mendaftarkan Router (Menempelkan fitur Auth dan ML ke aplikasi utama)
app.include_router(auth.router)
app.include_router(ml.router)