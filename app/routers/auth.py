from typing import Annotated, Optional
from fastapi import Depends, FastAPI, HTTPException, status, Form
from pydantic import BaseModel, EmailStr, constr, Field
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import APIRouter
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
import uuid
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

## INITIALIZE ROUTER
router = APIRouter()

#CREATE ADMIN
@router.post("/admin/new")
async def register_admin(
    user: str = Depends(get_current_user),  
    name: str = Form(None),
    dob: int = Form(None),
    national_id: int = Form(None),
    tax_number: int = Form(None),
    sex: bool = Form(None),
    address: Optional[str] = Form(None),
    email: EmailStr = Form(None),
    phone_num: int = Form(None),
    password: str = Form(None),
    user_name: str = Form(None),
    db=Depends(get_db)
):
    # Check if the authenticated user is an admin
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Only admins can create new admins")

    # Check for duplicate email
    existing_user = db.query(User).filter(User.user_email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = str(uuid.uuid4())  # Generate a UUID for user_id
        admin_id = str(uuid.uuid4())  # Generate a UUID for admin_id
        dob_datetime = datetime.fromtimestamp(dob)
        password_hash = get_password_hash(password)
        user = User(user_id=user_id, user_name=user_name, user_email=email, password=password_hash, user_type=1)
        admin = Admin(admin_id=admin_id, user_id=user_id,
                      name=name, dob=dob_datetime,
                      national_id=national_id, tax_number=tax_number,
                      phone_num=phone_num, sex=sex, address=address)
        db.add(user)
        db.add(admin)
        db.commit()
        db.refresh(user)
        db.refresh(admin)
        return admin
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


#REGISTER NEW PATIENT
@router.post("/patient/new")
async def register_patient(
    name: str = Form(None),
    dob: int = Form(None),
    national_id: int = Form(None),
    sex: bool = Form(None),
    phone_num: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    alias: Optional[str] = Form(None),
    relative_phone: Optional[str] = Form(None),
    insurance_id: Optional[str] = Form(None),
    email: EmailStr = Form(None),
    password: str = Form(None),
    user_name: str = Form(None),
    current_user: User = Depends(get_current_user),  # Use current_user instead of user
    db: Session = Depends(get_db)  # Use Session type hint for db
):
    # Ensure only admin or doctor can register a new patient
    if current_user.user_type not in [1, 2]:
        raise HTTPException(status_code=403, detail="Access forbidden. Only admins and doctors can register patients.")
    
    # Check for duplicate email
    existing_user = db.query(User).filter(User.user_email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    try:
        user_id = str(uuid.uuid4())  # Generate a UUID for user_id
        patient_id = str(uuid.uuid4())  # Generate a UUID for patient_id

        dob_datetime = datetime.fromtimestamp(dob)
        password_hash = get_password_hash(password)

        new_user = User(
            user_id=user_id,
            user_name=user_name,
            user_email=email,
            password=password_hash,
            user_type=4
        )
        
        new_patient = Patient(
            patient_id=patient_id,
            user_id=user_id,
            name=name,
            dob=dob_datetime,
            national_id=national_id,
            sex=sex,
            phone_num=phone_num,
            address=address,
            alias=alias,
            relative_phone=relative_phone,
            insurance_id=insurance_id
        )
        
        db.add(new_user)
        db.add(new_patient)
        db.commit()
        db.refresh(new_user)
        db.refresh(new_patient)
        return new_patient
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

    

## LOGIN SETUP
class Token(BaseModel):
    access_token: str
    token_type: str
    
def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(days=2) ##Sementara aku buat 2 hari (Chr)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, os.environ['SECRET_KEY'], algorithm=os.environ['ALGORITHM'])
    return encoded_jwt

def authenticate_user(user_email: str, password: str, db: Session):
    user = db.query(User).filter(User.user_email == user_email).first()
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

@router.post("/oauth/client/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db)
):
    user = authenticate_user(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(hours=int(os.environ['ACCESS_TOKEN_EXPIRE_HOURS']))
    access_token = create_access_token(
        data={"sub": user.user_email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/auth/me")
async def verify_identity(
    user: str = Depends(get_current_user),
):
    return user


@router.get("/user/list")
async def view_user(
    db: Session = Depends(get_db)
):
    try:
        insurances = db.query(User).all()
        if not insurances:
            raise HTTPException(status_code=404, detail="No USERS found")
        return insurances
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    

