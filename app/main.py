import uvicorn
from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware, db

from schema import *
import models
from starlette.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles

from routers import auth, data_query, doctor_staff

load_dotenv('.env')


app = FastAPI() 
app.mount('/static', StaticFiles(directory=os.environ['ASSET_STORAGE']), name="static")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "hello world"}

app.include_router(auth.router)
app.include_router(data_query.router)
app.include_router(doctor_staff.router)

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)