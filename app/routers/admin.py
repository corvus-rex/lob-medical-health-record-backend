from typing import Annotated, Optional, Dict
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile, Header
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


#GET LIST ADMIN
@router.get("/admin/list")
async def view_admin(
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    try:
        if current_user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")

        admins = db.query(Admin).all()
        if not admins:
            raise HTTPException(status_code=404, detail="No admins found")
        return admins
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    
#GET ADMIN BY ADMIN_ID
@router.get("/admin/{admin_id}")
async def get_admin_by_id(
    admin_id: str, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        # Check if the current user is an admin
        if current_user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden. Only admins can access this endpoint.")

        admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        return admin
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
#UPDATE ADMIN
@router.put("/admin/{admin_id}")
async def update_admin(
    admin_id: str,
    name: str = Form(None),
    pob: str = Form(None),
    dob: int = Form(None),
    national_id: int = Form(None),
    tax_number: int = Form(None),
    sex: bool = Form(None),
    address: str = Form(None),
    phone_num: int = Form(None),
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        # Check if the current user is an admin
        if current_user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden. Only admins can update admin information.")

        admin = db.query(Admin).filter(Admin.admin_id == admin_id).first()
        if not admin:
            raise HTTPException(status_code=404, detail="Admin not found")
        
        # Update admin information
        if name is not None:
            admin.name = name
        if pob is not None:
            admin.pob = pob
        if dob is not None:
            admin.dob = datetime.fromtimestamp(dob)
        if national_id is not None:
            admin.national_id = national_id
        if tax_number is not None:
            admin.tax_number = tax_number
        if sex is not None:
            admin.sex = sex
        if address is not None:
            admin.address = address
        if phone_num is not None:
            admin.phone_num = phone_num

        db.commit()
        db.refresh(admin)
        return admin
    except Exception as e:
        raise HTTPException(status_code=500, detail=str("Internel Server Error"))


##GET LIST PATIENT
@router.get("/patient/list")
async def view_patient(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if the user is an admin or doctor
        if current_user.user_type not in [1, 2]:
            raise HTTPException(status_code=403, detail="Access forbidden")
        
        patients = db.query(Patient).all()
        if not patients:
            raise HTTPException(status_code=404, detail="No patients found")
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


#GET PATIENT DATA BY ID
@router.get("/patient/{patient_id}")
async def get_patient_by_id(
    patient_id: str, 
    current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)
):
    try:
        # Fetch patient data
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        
        # Check if the user is an admin, doctor, or the patient themselves
        if current_user.user_type not in [1, 2] and current_user.user_id != patient.user_id:
            raise HTTPException(status_code=403, detail="Access forbidden")

        # Fetch medical record
        medical_record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.patient_id).first()
        if not medical_record:
            medical_record = None 

        medical_record.medical_note = db.query(MedicalNote).filter(MedicalNote.record_id == medical_record.record_id).all()
        medical_record.clinical_entry = db.query(ClinicalEntry).filter(ClinicalEntry.record_id == medical_record.record_id).all()
        medical_record.lab_report = db.query(LabReport).filter(LabReport.record_id == medical_record.record_id).all()

        return {
            'patient': patient,
            'medical_record': medical_record,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

#UPDATE PATIENT
@router.put("/patient/{patient_id}")
async def update_patient(
    patient_id: str,
    name: str = Form(None),
    dob: int = Form(None),
    national_id: int = Form(None),
    sex: bool = Form(None),
    phone_num: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    alias: Optional[str] = Form(None),
    relative_phone: Optional[str] = Form(None),
    insurance_id: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        # Check if the user is an admin or doctor
        if current_user.user_type not in [1, 2]:
            raise HTTPException(status_code=403, detail="Access forbidden")

        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        if name is not None:
            patient.name = name
        if dob is not None:
            patient.dob = datetime.fromtimestamp(dob)
        if national_id is not None:
            patient.national_id = national_id
        if sex is not None:
            patient.sex = sex
        if phone_num is not None:
            patient.phone_num = phone_num
        if address is not None:
            patient.address = address
        if alias is not None:
            patient.alias = alias
        if relative_phone is not None:
            patient.relative_phone = relative_phone
        if insurance_id is not None:
            patient.insurance_id = insurance_id

        db.commit()
        db.refresh(patient)
        return patient
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

    

# REGISTER NEW INSURANCE
@router.post("/insurance/new")
async def register_insurance(
    insurance_name: str = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:  # Ensure the user is an admin
        raise HTTPException(status_code=403, detail="Access forbidden")

    existing_insurance = db.query(Insurance).filter(Insurance.insurance_name == insurance_name).first()
    if existing_insurance:
        raise HTTPException(status_code=400, detail="This insurance name already exists")

    try:
        insurance_id = str(uuid.uuid4())  # Generate a UUID for insurance

        insurance = Insurance(insurance_id=insurance_id, insurance_name=insurance_name)
        db.add(insurance)
        db.commit()
        db.refresh(insurance)
        return insurance
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    
# GET LIST OF INSURANCE
@router.get("/insurance/list")
async def view_insurance(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:  # Ensure the user is an admin
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        insurances = db.query(Insurance).all()
        if not insurances:
            raise HTTPException(status_code=404, detail="No insurances found")
        return insurances
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# GET INSURANCE BY ID
@router.get("/insurance/{insurance_id}")
async def get_insurance_by_id(
    insurance_id: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:  # Ensure the user is an admin
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        insurance = db.query(Insurance).filter(Insurance.insurance_id == insurance_id).first()
        if not insurance:
            raise HTTPException(status_code=404, detail="Insurance not found")
        return insurance
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# UPDATE INSURANCE
@router.put("/insurance/{insurance_id}")
async def update_insurance(
    insurance_id: str,
    insurance_name: str = Form(None),
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:  # Ensure the user is an admin
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        insurance = db.query(Insurance).filter(Insurance.insurance_id == insurance_id).first()
        if not insurance:
            raise HTTPException(status_code=404, detail="Insurance not found")

        if insurance_name is not None:
            insurance.insurance_name = insurance_name

        db.commit()
        db.refresh(insurance)
        return insurance
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")



