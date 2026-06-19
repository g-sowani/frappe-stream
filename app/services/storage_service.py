# app/services/storage_service.py
import os, shutil, aiofiles
from app.config import settings

class StorageService:
    """
    Backend: local filesystem now.
    Stub: MinIO, S3 — swap by changing config.
    Interface never changes.
    """
    
    def get_raw_path(self, video_id: str) -> str:
        path = f"{settings.storage_path}/raw/{video_id}"
        os.makedirs(path, exist_ok=True)
        return f"{path}/original.mp4"
    
    def get_hls_dir(self, video_id: str) -> str:
        path = f"{settings.storage_path}/hls/{video_id}"
        os.makedirs(path, exist_ok=True)
        return path
    
    def get_thumbnail_path(self, video_id: str) -> str:
        path = f"{settings.storage_path}/thumbnails"
        os.makedirs(path, exist_ok=True)
        return f"{path}/{video_id}.jpg"
    
    def get_manifest_url(self, video_id: str) -> str:
        backend = settings.cdn_backend
        if backend == "local":
            return f"/stream/hls/{video_id}/master.m3u8"
        # stub — CDN URL generation
        raise NotImplementedError(f"CDN backend {backend} not implemented")
    
    def delete_raw(self, video_id: str):
        raw_path = self.get_raw_path(video_id)
        if os.path.exists(raw_path):
            os.remove(raw_path)
    
    # Stubs for scale
    def migrate_to_minio(self, video_id: str):
        raise NotImplementedError("MinIO migration — v2")
    
    def migrate_to_s3(self, video_id: str):
        raise NotImplementedError("S3 migration — v2")