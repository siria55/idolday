import threading
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.routers import api_router

from jobs import gen_voice_token

from mqtt.mqtt_listener import mqtt_listener_run


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://setup.toaitoys.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request, exc):
    errs = exc.errors()
    
    if errs and 'type' in errs[0]:
        print('11111')
        print('errs[0] = ', errs[0])
        res = {
            'code': 4000,
            'message': '参数错误',
            'data': {}
        }
    else:
        res = {
            'code': 1000,
            'message': '未知错误',
            'data': {}
        }
    return JSONResponse(content=res)

app.include_router(api_router, prefix="/api/v1")
app.mount("/static", StaticFiles(directory="static"), name="static")

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


if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8001, reload=True)
