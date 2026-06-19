from fastapi import FastAPI
from app.db.session import engine, Base
# These two imports are critical — they register the models with Base
from app.models import user, video  
from app.api.v1 import auth, video as video_router, stream

app = FastAPI(title="Frappe Stream")

# runs on startup before accepting any requests
@app.on_event("startup")
async def startup():
    # with is for cleanup
    async with engine.begin() as conn:
        # looks at every class inherited from Base like video and user right now.
        # checks if table exists in postgresql, creates if not present

        await conn.run_sync(Base.metadata.create_all)

# register all routes from each file
app.include_router(auth.router)
app.include_router(video_router.router)
app.include_router(stream.router)