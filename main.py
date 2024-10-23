import threading
import uvicorn
import os

from fastapi import FastAPI
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError, HTTPException
from fastapi.staticfiles import StaticFiles

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from api.routers import api_router


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

# scheduler = AsyncIOScheduler()

if __name__ == '__main__':
    uvicorn.run('main:app', host="0.0.0.0", port=8000, workers=1, reload=True)
