from typing import Annotated, Optional, Dict
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile
from pydantic import BaseModel, EmailStr, constr, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from datetime import datetime, timedelta
from passlib.context import CryptContext

import uuid
import json
import os
from dotenv import load_dotenv

from schema import *
from models import *

load_dotenv('.env')

## SET UP CRYPTO CONTEXT
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

ASSET_STORAGE = os.environ['ASSET_STORAGE']

## INITIALIZE ROUTER
router = APIRouter()

#REGISTER NEW USER
@router.post("/user/new")
async def register_user(
    user_name: str = Form(None),
    user_type: int = Form(None),
    user_email: str = Form(None),
    password: str = Form(None),
    db=Depends(get_db)
):
    ## Check for duplicate email
    existing_user = db.query(User).filter(User.user_email == user_email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        user_id = str(uuid.uuid4())  # Generate a UUID for user_id
        password_hash = get_password_hash(password)
        
        # Create a new user instance
        new_user = User(
            user_id=user_id,
            user_name=user_name,
            user_type=user_type,
            user_email=user_email,
            password=password_hash
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    
##VIEW ALL PATIENTS
@router.get("/patient/list")
async def view_patient(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        if current_user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")

        patients = db.query(Patient).all()
        if not patients:
            raise HTTPException(status_code=404, detail="No patients found")
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


