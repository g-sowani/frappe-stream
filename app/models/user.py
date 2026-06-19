from sqlalchemy import Column, String, DateTime, Boolean

from sqlalchemy.sql import func
# import base from session.py - engine knows about this base 
from app.db.session import Base
import uuid

class User(Base) :
    __tablename__ = "users" # actual table name in PostgreSQL

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4())) # fresh uuid for each new user.
    email      = Column(String(255), unique=True, nullable=False, index=True) 
    username   = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False) # bcrypt hashes - always 60 characters but 255 gives headroom for future algorithm changes
    is_active  = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now()) # postgresql sets this automatically.