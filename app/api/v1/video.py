from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid, os, aiofiles

from app.db.session import get_db
from app.models.video import Video, VideoStatus
from app.models.user import User
from app.core.dependencies import get_current_user
from app.services.storage_service import StorageService
from app.workers.video_tasks import process_video
from app.config import settings

router = APIRouter(prefix="/api/v1/videos", tags=["videos"])
storage = StorageService()

ALLOWED_TYPES = {"video/mp4", "video/quicktime", "video/x-matroska"}
MAX_SIZE = 2 * 1024 * 1024 * 1024  # 2GB


@router.post("/upload")
async def upload_video(
    title: str = Form(...), # from multipart form data NOT JSON. (...) means required.
    description: str = Form(""),  # optional, defaults to empty
    file: UploadFile = File(...),  # not json. 
    current_user: User = Depends(get_current_user), # inversion of control
    db: AsyncSession = Depends(get_db)
):
    # Validate
    # reject non-video content types before saving 
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(400, f"Unsupported format: {file.content_type}")
    
    # Create video record
    # db record for video is created - before saving file.
    # mark as failed if save fails.
    # avoids orphaned file with no record if save done and then db record insert fails
    video_id = str(uuid.uuid4())
    video = Video(
        id=video_id,
        title=title,
        description=description,
        owner_id=current_user.id,
        status=VideoStatus.processing
    )
    db.add(video)
    await db.commit()
    
    # Save file to disk
    dest_path = storage.get_raw_path(video_id) # store to video_id path
    
    async with aiofiles.open(dest_path, "wb") as f: # async
        total_size = 0
        while chunk := await file.read(1024 * 1024):  # read in 1MB chunks
            total_size += len(chunk)
            if total_size > MAX_SIZE: # size of file cant exceed 2GB if it does - scrap.
                os.remove(dest_path) # delete partial file and reject
                raise HTTPException(400, "File too large")
            # if all's good, write to disk
            await f.write(chunk) 
    
    # Update file size
    video.file_size_bytes = total_size
    await db.commit()
    
    # Enqueue processing job - drop job in queue
    # FFmpeg will run in bg on a seperate process.
    process_video.delay(video_id)
    
    return {
        # this is returned immediately. user gets response in ms
        "video_id": video_id,
        "status": "processing",
        "message": "Upload received. Processing started."
    }

# retrieving video
@router.get("/{video_id}")
async def get_video(
    video_id: str,
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(select(Video).where(Video.id == video_id))
    video = result.scalar_one_or_none()
    
    if not video:
        raise HTTPException(404, "Video not found")
    
    return {
        "id": video.id,
        "title": video.title,
        "description": video.description,
        "status": video.status,
        "duration": video.duration_seconds,
        "views": video.views,
        "manifest_url": storage.get_manifest_url(video.id) if video.status == VideoStatus.published else None,
        "thumbnail_url": f"/stream/thumbnails/{video.id}.jpg" if video.thumbnail_path else None,
        "created_at": str(video.created_at)
    }

@router.get("/")
async def list_videos(db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Video)
        .where(Video.status == VideoStatus.published)
        .order_by(Video.created_at.desc())
        .limit(20)
    )
    videos = result.scalars().all()
    return [
        {
            "id": v.id,
            "title": v.title,
            "status": v.status,
            "duration": v.duration_seconds,
            "views": v.views,
            "thumbnail_url": f"/stream/thumbnails/{v.id}.jpg" if v.thumbnail_path else None,
            "manifest_url": storage.get_manifest_url(v.id)
        }
        for v in videos
    ]
