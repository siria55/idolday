import os
import threading
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.routers import api_router

from jobs import gen_voice_token

from mqtt.mqtt_listener import mqtt_listener_run


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://setup.toaitoys.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")

scheduler = AsyncIOScheduler()
gen_voice_token()
scheduler.add_job(gen_voice_token, 'interval', seconds=60 * 60 * 10)

# 使用FastAPI的事件处理器启动MQTT客户端
@app.on_event("startup")
async def startup_event():
    print('startup')
    mqtt_thread = threading.Thread(target=mqtt_listener_run)
    mqtt_thread.start()
    print('mqtt_thread started')
