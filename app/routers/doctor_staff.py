from typing import Annotated, Optional, Dict
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile
from pydantic import BaseModel, EmailStr, constr, Field, create_model
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_sqlalchemy import DBSessionMiddleware, db
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from dependencies import get_db, get_current_user
from passlib.context import CryptContext
from jose import JWTError, jwt
from datetime import datetime, timedelta
from moviepy.editor import VideoFileClip
from pydub import AudioSegment
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

#REGISTER NEW DOCTOR
@router.post("/doctor/register")
async def register_doctor(
    name: str = Form(None),
    dob: int=Form(None),
    national_id: int=Form(None),
    phone_num: int=Form(None),
    tax_num: int=Form(None),
    pob: str=Form(None),
    license_num: int=Form(None),
    historical: Dict | str = Form(None),
    address: Optional[str]=Form(None),
    sex: bool=Form(None),
    email: EmailStr= Form(None),
    password: str=Form(None),
    user_name: str=Form(None),
    db=Depends(get_db)
):
    
    ## Check for duplicate email
    existing_user = db.query(User).filter(User.user_email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = str(uuid.uuid4())  # Generate a UUID for user_id
        doctor_id = str(uuid.uuid4()) # Generate a UUID for admin_id
        dob_datetime = datetime.fromtimestamp(dob)
        password_hash = get_password_hash(password)
        
        if isinstance(historical, str):
            # Convert string to dictionary
            data_dict = json.loads(historical)
        else:
            # Assume it's already a dictionary
            data_dict = historical

        dynamic_fields = {key: (type(value), ...) for key, value in data_dict.items()}

        # Create a dynamic model class
        DynamicModel = create_model('DynamicModel', **dynamic_fields)

        # Create an instance of the dynamic model
        dynamic_instance = DynamicModel(**data_dict).json()

        user = User(user_id=user_id, user_name=user_name, user_email=email, password=password_hash, user_type=2)
        doctor = Doctor(doctor_id=doctor_id, user_id=user_id, 
                      name=name, dob=dob_datetime, 
                      national_id=national_id, tax_num=tax_num,
                      license_num=license_num, historical=dynamic_instance,
                      pob=pob, phone_num=phone_num, sex=sex, address=address)
        db.add(user)
        db.add(doctor)
        db.commit()
        db.refresh(user)
        db.refresh(doctor)
        return doctor
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

#REGISTER NEW STAFF
@router.post("/staff/register")
async def register_staff(
    name: str = Form(None),
    dob: int=Form(None),
    pob: str=Form(None),
    national_id: int=Form(None),
    phone_num: int=Form(None),
    tax_num: int=Form(None),
    license_num: int=Form(None),
    historical: Dict | str = Form(None),
    address: Optional[str]=Form(None),
    sex: bool=Form(None),
    email: EmailStr= Form(None),
    password: str=Form(None),
    user_name: str=Form(None),
    db=Depends(get_db)
):
    
    ## Check for duplicate email
    existing_user = db.query(User).filter(User.user_email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = str(uuid.uuid4())  # Generate a UUID for user_id
        staff_id = str(uuid.uuid4()) # Generate a UUID for admin_id
        dob_datetime = datetime.fromtimestamp(dob)
        password_hash = get_password_hash(password)
        
        if isinstance(historical, str):
            # Convert string to dictionary
            data_dict = json.loads(historical)
        else:
            # Assume it's already a dictionary
            data_dict = historical

        dynamic_fields = {key: (type(value), ...) for key, value in data_dict.items()}

        # Create a dynamic model class
        DynamicModel = create_model('DynamicModel', **dynamic_fields)

        # Create an instance of the dynamic model
        dynamic_instance = DynamicModel(**data_dict).json()

        
        user = User(user_id=user_id, user_name=user_name, user_email=email, password=password_hash, user_type=3)
        staff = MedicalStaff(staff_id=staff_id, user_id=user_id, 
                      name=name, dob=dob_datetime, pob=pob,
                      national_id=national_id, tax_num=tax_num,
                      license_num=license_num, historical=dynamic_instance,
                      phone_num=phone_num, sex=sex, address=address)
        db.add(user)
        db.add(staff)
        db.commit()
        db.refresh(user)
        db.refresh(staff)
        return staff
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

#REGISTER NEW POLYCLINIC
@router.post("/polyclinic/register")
async def register_polyclinic(
    poly_name: str = Form(None),
    poly_desc: str = Form(None),
    db=Depends(get_db)
):
    
    ## Check for duplicate polyclinic name
    existing_poly = db.query(Polyclinic).filter(Polyclinic.poly_name == poly_name).first()
    if existing_poly:
        raise HTTPException(status_code=400, detail="This polyclinic name already exist")
    
    try:
        poly_id = str(uuid.uuid4())  # Generate a UUID for polyclinic
        
        polyclinic = Polyclinic(poly_id=poly_id, poly_name=poly_name, poly_desc=poly_desc)
        db.add(polyclinic)
        db.commit()
        db.refresh(polyclinic)
        return polyclinic
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    

#REGISTER NEW LABORATORY
@router.post("/laboratory/register")
async def register_laboratory(
    lab_name: str = Form(None),
    lab_desc: str = Form(None),
    db=Depends(get_db)
):
    
    ## Check for duplicate polyclinic name
    existing_poly = db.query(Laboratory).filter(Laboratory.lab_name == lab_name).first()
    if existing_poly:
        raise HTTPException(status_code=400, detail="This laboratory name already exist")
    
    try:
        lab_id = str(uuid.uuid4())  # Generate a UUID for laboratory
        
        laboratory = Laboratory(lab_id=lab_id, lab_name=lab_name, lab_desc=lab_desc)
        db.add(laboratory)
        db.commit()
        db.refresh(laboratory)
        return laboratory
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    
#REGISTER DOCTOR TO POLYCLINIC
@router.post("/polyclinic/doctor/register")
async def register_doctor_polyclinic(
    poly_id: str=Form(None),
    doctor_id: str=Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    ## Only Admin can register doctor to existing polyclinic
    if user.user_type != 1:
        raise HTTPException(status_code=401, detail="Authorization error: Only admin can register new doctor to polyclinic")

    ## Check if poly_id exist
    existing_poly = db.query(Polyclinic).filter(str(Polyclinic.poly_id) == poly_id).first()
    if not existing_poly:
        raise HTTPException(status_code=400, detail="This polyclinic ID does not exist")

    ## Check if doctor_id exist
    existing_doctor = db.query(Doctor).filter(str(Doctor.doctor_id) == doctor_id).first()
    if not existing_doctor:
        raise HTTPException(status_code=400, detail="This doctor ID does not exist")
    
    try:        
        doctor_poly = PolyclinicDoctor(poly_id=poly_id, doctor_id=doctor_id)
        db.add(doctor_poly)
        db.doctor_poly()
        db.refresh(doctor_poly)
        return doctor_poly
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


#REGISTER STAFF TO LABORATORY
@router.post("/laboratory/staff/register")
async def register_doctor_polyclinic(
    lab_id: str=Form(None),
    staff_id: str=Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    ## Only Admin can register staff to existing laboratory
    if user.user_type != 1:
        raise HTTPException(status_code=401, detail="Authorization error: Only admin can register new staff to laboratory")

    ## Check if lab_id exist
    existing_lab = db.query(Laboratory).filter(str(Laboratory.lab_id) == lab_id).first()
    if not existing_lab:
        raise HTTPException(status_code=400, detail="This laboratory ID does not exist")

    ## Check if doctor_id exist
    existing_staff = db.query(MedicalStaff).filter(str(MedicalStaff.staff_id) == staff_id).first()
    if not existing_staff:
        raise HTTPException(status_code=400, detail="This staff ID does not exist")
    
    try:        
        staff_laboratory = LaboratoryStaff(lab_id=lab_id, staff_id=staff_id)
        db.add(staff_laboratory)
        db.doctor_poly()
        db.refresh(staff_laboratory)
        return staff_laboratory
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")