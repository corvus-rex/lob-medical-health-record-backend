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

##GET LIST PATIENT
@router.get("/patient/list")
async def view_patient(
    # current_user: User = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    try:
        # if current_user.user_type != 1:
        #     raise HTTPException(status_code=403, detail="Access forbidden")

        patients = db.query(Patient).all()
        if not patients:
            raise HTTPException(status_code=404, detail="No patients found")
        return patients
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

#GET PATIENT DATA BY ID
@router.get("/patient/{patient_id}")
async def get_patient_by_id(patient_id: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    try:
        # Fetch patient data
        patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")

        # Fetch medical record
        medical_record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient.patient_id).first()
        if not medical_record:
            medical_record = None 

        # Fetch lab reports
        lab_reports = []
        if medical_record:
            lab_reports = db.query(LabReport).filter(LabReport.record_id == medical_record.record_id).all()
        else:
            lab_reports = []

        # Fetch medical notes
        medical_notes = []
        if medical_record:
            medical_notes = db.query(MedicalNote).filter(MedicalNote.record_id == medical_record.record_id).all()
        else:
            medical_notes = []

        # Fetch clinical entry
        clinical_entries = []
        if medical_record:
            clinical_entries = db.query(ClinicalEntry).filter(ClinicalEntry.record_id == medical_record.record_id).all()
        else:
            clinical_entries = []

        return {
            'patient': patient,
            'medical_record': medical_record,
            'lab_report': lab_reports,
            'medical_note': medical_notes,
            'clinical_entry': clinical_entries
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


