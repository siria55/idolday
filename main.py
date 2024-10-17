import threading
import uvicorn
import os

from fastapi import FastAPI
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
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
        print('errs[0] = ', errs[0])
        msg = errs[0]['msg']
        if ',' in msg:
            msg = msg.split(',')[1].strip()
        else:
            msg = str(errs[0]['loc']) + ' ' + msg
        res = {
            'code': 4000,
            'message': msg,
            'data': {}
        }
    else:
        res = {
            'code': 1000,
            'message': '未知错误',
            'data': {}
        }
    return JSONResponse(content=res)

@app.exception_handler(HTTPException)
def http_exception_handler(request, exc):
    if exc.status_code == 401:
        res = {
            'code': 10000,
            'message': '认证失败，请重新登录',
            'data': {}
        }
        print('in http_exception_handler')
        return JSONResponse(content=res)
    raise exc

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

# from fastapi.templating import Jinja2Templates
# app.mount("/static", StaticFiles(directory="static"), name="static")
# templates = Jinja2Templates(directory="templates")
# @app.get("/static", response_class=HTMLResponse)
# def list_files(request: Request):

#     files = os.listdir("./static")
#     files_paths = sorted([f"{request.url._url}/{f}" for f in files])
#     print(files_paths)
#     return templates.TemplateResponse(
#         "list_files.html", {"request": request, "files": files_paths}
#     )

# from starlette.testclient import TestClient
# def test_app():
#     client = TestClient(app)
#     client.post("/api/v1/user/login", json={"username": "foo", "password": "bar"})

if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8001, reload=True)
