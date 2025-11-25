import bcrypt

def get_password_hash(password: str) -> str:
    """Mengubah password biasa menjadi kode acak (hash)"""
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pwd_bytes, salt)
    return hashed.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Mengecek apakah password input cocok dengan hash di DB"""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))