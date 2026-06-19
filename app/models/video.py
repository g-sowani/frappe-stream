from sqlalchemy import Column, String, Integer, BigInteger, Float
from sqlalchemy import DateTime, Text, ForeignKey, Index, Enum
from sqlalchemy.sql import func
from app.db.session import Base
import uuid, enum 

class VideoStatus(str, enum.Enum):
    awaiting_upload = "awaiting_upload"
    processing = "processing"
    published = "published"
    failed = "failed"

class Video(Base):
    __tablename__ = "videos"
    id               = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title            = Column(String(500), nullable=False)
    description      = Column(Text)
    owner_id         = Column(String(36), ForeignKey("users.id"), nullable=False)
    
    raw_file_path    = Column(String(1000))
    file_size_bytes  = Column(BigInteger)
    status           = Column(Enum(VideoStatus), default=VideoStatus.awaiting_upload, index=True)
    failure_reason   = Column(Text)
    status_updated_at = Column(DateTime, onupdate=func.now())
    
    duration_seconds = Column(Float)
    thumbnail_path   = Column(String(1000))
    
    views            = Column(BigInteger, default=0)
    like_count       = Column(Integer, default=0)
    
    created_at       = Column(DateTime, server_default=func.now())
    published_at     = Column(DateTime)
    
    __table_args__ = (
        Index("ix_videos_status_created", "status", "created_at"),
    )
