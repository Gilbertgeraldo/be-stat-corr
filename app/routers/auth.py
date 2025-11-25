from fastapi import APIRouter, HTTPException
from app.database import supabase
from app.models import UserAuth
from app.utils.security import get_password_hash, verify_password
import re

router = APIRouter(tags=["Authentication"])

@router.post("/register")
def register_manual(user: UserAuth):
    try:
        # Validasi Email Regex
        email_pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(email_pattern, user.email):
            raise HTTPException(status_code=400, detail="Format email salah!")

        # Cek Email Duplikat
        existing_user = supabase.table("users").select("*").eq("email", user.email).execute()
        if len(existing_user.data) > 0:
            raise HTTPException(status_code=400, detail="Email sudah terdaftar!")

        # Hash Password & Insert
        hashed_password = get_password_hash(user.password)
        
        data_insert = {
            "email": user.email,
            "password": hashed_password
        }
        supabase.table("users").insert(data_insert).execute()
        
        return {"message": "Registrasi Berhasil! Silakan Login."}

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/login")
def login_manual(user: UserAuth):
    try:
        # Cari User
        response = supabase.table("users").select("*").eq("email", user.email).execute()
        
        if len(response.data) == 0:
            raise HTTPException(status_code=400, detail="Email atau Password salah")
        
        user_data = response.data[0]

        # Verifikasi Password
        is_valid = verify_password(user.password, user_data["password"])
        if not is_valid:
            raise HTTPException(status_code=400, detail="Email atau Password salah")

        return {
            "message": "Login Berhasil", 
            "user_id": user_data["id"],
            "email": user_data["email"]
        }

    except Exception as e:
        if isinstance(e, HTTPException): raise e
        raise HTTPException(status_code=500, detail=str(e))