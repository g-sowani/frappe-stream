cat > README.md << 'EOF'
# Frappe Stream

A self-hostable video streaming platform built with FastAPI, PostgreSQL, Redis, FFmpeg, and HLS.

## Architecture

- **FastAPI** — async REST API
- **PostgreSQL** — metadata storage (videos, users)
- **Redis** — job queue + analytics buffer
- **Celery** — background video processing workers
- **FFmpeg** — video transcoding + HLS segment generation
- **Video.js** — HLS player with adaptive bitrate streaming

## Stack

| Concern | Technology |
|---|---|
| API | FastAPI + Python |
| Database | PostgreSQL + SQLAlchemy |
| Queue | Celery + Redis |
| Processing | FFmpeg (HLS, thumbnails, ABR) |
| Storage | Local FS → MinIO → S3 (pluggable) |
| Streaming | HLS with adaptive bitrate (240p/480p/720p) |
| Auth | JWT (python-jose + bcrypt) |

## Setup

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# edit .env with your database credentials

# Run
uvicorn app.main:app --reload          # API server
celery -A app.workers.celery_app worker # Background worker
```

## Status

Building toward a production-grade video platform with:
- HLS streaming with adaptive bitrate
- Background FFmpeg processing pipeline
- Pluggable storage (local → MinIO → S3)
- Redis-buffered analytics
- Recommendation engine (in progress)
EOF