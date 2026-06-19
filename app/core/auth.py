# app/core/auth.py
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from app.config import settings

pwd_context = CryptContext(schemes=["bcrypt"])

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# hash what user typed and compare it with the hash that is stored
# since bcrypt will hash same password in the exact same way.
# if db stolen - attackers now have the hashed passwords which cant be reversed so of no use 
# must know real passwords to check
def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(user_id: str) -> str:
    payload = {
        "sub": user_id, # the actual data 
        "exp": datetime.utcnow() + timedelta(hours=24) # 24 hours
    }
    return jwt.encode(payload, settings.secret_key, algorithm="HS256")

def decode_token(token: str) -> str:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
        return payload["sub"]
    except JWTError:
        raise ValueError("Invalid token")