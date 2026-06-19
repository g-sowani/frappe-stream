# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from app.core.auth import hash_password, verify_password, create_access_token
from sqlalchemy import select
import uuid

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])

class RegisterRequest(BaseModel):
    email: str
    username: str
    password: str

class LoginRequest(BaseModel):
    email: str
    password: str

@router.post("/register")
async def register(request: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        username=request.username,
        hashed_password=hash_password(request.password)
    )
    db.add(user)
    await db.commit()
    return {"message": "registered", "user_id": user.id}

@router.post("/login")
async def login(request: LoginRequest, db: AsyncSession = Depends(get_db)):
    # find user by email
    result = await db.execute(select(User).where(User.email == request.email)) 
    # return user object if found else none 
    # error never raised for missing rows 
    user = result.scalar_one_or_none()
    
    # error - we say invalid email or password 
    # never say wrong email and wrong password 
    # leaks information about which emails are registered.
    if not user or not verify_password(request.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    return {"access_token": create_access_token(user.id)}