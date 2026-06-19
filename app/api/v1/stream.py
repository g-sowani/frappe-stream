# app/api/v1/auth.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from app.db.session import get_db
from app.models.user import User
from sqlalchemy import select
import uuid

router = APIRouter(prefix="/api/v1/stream", tags=["stream"])
