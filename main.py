import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.schedulers.background import BackgroundScheduler
import asyncio

from api.routers import api_router
from api import get_current_user, decode_token
from models import User

from jobs import gen_voice_token



app = FastAPI()
app.include_router(api_router, prefix="/api/v1")

scheduler = AsyncIOScheduler()
gen_voice_token()
scheduler.add_job(gen_voice_token, 'interval', seconds=60 * 60 * 10)

@app.get("/download/audio_res/{filename}", tags=["Download"])
async def download_file(filename: str, token: str = Depends(get_current_user)):
    phone_number = decode_token(token)
    user = User.get(phone_number)
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    headers={
        "Content-Disposition": f"attachment; filename={filename}"
    }
    return FileResponse(
        os.path.join('audio_res', filename), headers=headers,
        media_type='application/octet-stream')

