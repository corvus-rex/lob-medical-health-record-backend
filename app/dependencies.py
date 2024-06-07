from fastapi import Depends
from database import SessionLocal
from fastapi import FastAPI, Header, HTTPException
from fastapi.security import APIKeyHeader
from jwt import decode, InvalidTokenError
from typing import Optional
import os
from dotenv import load_dotenv
from models import *

app = FastAPI()

load_dotenv('.env')

# Secret key for decoding JWT
SECRET_KEY = os.environ['SECRET_KEY']
ALGORITHM = os.environ['ALGORITHM']

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# X_API_KEY = APIKeyHeader(name='X-API-Key')

# SAMPLE USAGE
# @app.get("/protected")
# async def protected_route(user: str = Depends(get_current_user)):
#     return {"user_id": user}
# async def get_current_user(x_api_key: str = Depends(X_API_KEY), db = Depends(get_db)):
#     if x_api_key is None:
#         raise HTTPException(status_code=401, detail="X-API-Key header required")

#     try:
#         payload = decode(x_api_key, SECRET_KEY, algorithms=ALGORITHM)
#         user_email = payload.get("sub")

#         # Fetch user data from database or dictionary
#         user = db.query(User).filter(User.user_email == user_email).first()
#         if user is None:
#             raise HTTPException(status_code=401, detail="User not found")

#         return user
#     except InvalidTokenError:
#         raise HTTPException(status_code=401, detail="Invalid token")

async def get_current_user(authorization: str = Header(...), db=Depends(get_db)):
    if authorization is None or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Authorization header with Bearer token required")

    token = authorization.replace("Bearer ", "")
    
    try:
        payload = decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_email = payload.get("sub")

        # Fetch user data from database or dictionary
        user = db.query(User).filter(User.user_email == user_email).first()
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")

        return user
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
