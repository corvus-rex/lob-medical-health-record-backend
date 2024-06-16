from typing import Annotated, Optional, Dict
from fastapi import Depends, FastAPI, HTTPException, status, Form, UploadFile, File
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
import shutil


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
@router.post("/doctor/new")
async def register_doctor(
    name: str = Form(None),
    pob: str = Form(None),
    dob: int = Form(None),
    national_id: str = Form(None),
    phone_num: str = Form(None),
    tax_num: str = Form(None),
    license_num: str = Form(None),
    historical: Optional[str] = Form(None),
    address: Optional[str] = Form(None),
    sex: Optional[bool] = Form(None),
    email: EmailStr = Form(None),
    password: str = Form(None),
    user_name: str = Form(None),
    db: Session = Depends(get_db)
):
    # Check for duplicate email
    existing_user = db.query(User).filter(User.user_email == email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        user_id = str(uuid.uuid4())  # Generate a UUID for user_id
        doctor_id = str(uuid.uuid4()) # Generate a UUID for doctor_id
        dob_datetime = datetime.fromtimestamp(dob)
        password_hash = get_password_hash(password)
        
        if historical:
            try:
                # Convert string to dictionary
                data_dict = json.loads(historical)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON for historical field: {str(e)}")
        else:
            data_dict = {}

        # Create dynamic fields for the historical model
        dynamic_fields = {key: (type(value), ...) for key, value in data_dict.items()}
        DynamicModel = create_model('DynamicModel', **dynamic_fields)
        dynamic_instance = DynamicModel(**data_dict).json()

        user = User(user_id=user_id, user_name=user_name, user_email=email, password=password_hash, user_type=2)
        doctor = Doctor(
            doctor_id=doctor_id, user_id=user_id, 
            name=name, dob=dob_datetime, national_id=national_id, 
            tax_num=tax_num, license_num=license_num, 
            historical=dynamic_instance, pob=pob, 
            phone_num=phone_num, sex=sex, address=address
        )
        db.add(user)
        db.add(doctor)
        db.commit()
        db.refresh(user)
        db.refresh(doctor)
        return doctor
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
##GET LIST DOCTOR
@router.get("/doctor/list")
async def view_doctor(
    user: str = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden.")

        doctors = db.query(Doctor).all()
        if not doctors:
            raise HTTPException(status_code=404, detail="No doctors found")
        return doctors
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

##GET DOCTOR BY DOCTOR_ID
@router.get("/doctor/{doctor_id}")
async def get_doctor_by_id(
    doctor_id: str, 
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        if user.user_type not in [1, 2]:
            raise HTTPException(status_code=403, detail="Access forbidden")
        
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
        return doctor
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

##UPDATE DOCTOR
@router.put("/doctor/{doctor_id}")
async def update_doctor(
    doctor_id: str,
    name: str = Form(None),
    pob: str = Form(None),
    dob: int = Form(None),
    national_id: str = Form(None),
    phone_num: str = Form(None),
    tax_num: str = Form(None),
    license_num: str = Form(None),
    historical: str = Form(None),
    address: str = Form(None),
    sex: bool = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden.")
        
        doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")
    
        if name is not None:
            doctor.name = name
        if pob is not None:
            doctor.pob = pob
        if dob is not None:
            doctor.dob = datetime.fromtimestamp(dob)
        if national_id is not None:
            doctor.national_id = national_id
        if phone_num is not None:
            doctor.phone_num = phone_num
        if tax_num is not None:
            doctor.tax_num = tax_num
        if license_num is not None:
            doctor.license_num = license_num
        if historical is not None:
            doctor.historical = historical
        if address is not None:
            doctor.address = address
        if sex is not None:
            doctor.sex = sex

        db.commit()
        db.refresh(doctor)
        return doctor
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

#REGISTER NEW STAFF
@router.post("/staff/new")
async def register_staff(
    name: str = Form(None),
    dob: int = Form(None),  
    pob: str = Form(None),
    national_id: str = Form(None),  
    phone_num: str = Form(None),  
    tax_num: str = Form(None),  
    license_num: str = Form(None),  
    historical: Dict | str = Form(None),
    address: Optional[str] = Form(None),
    sex: bool = Form(None),
    email: EmailStr = Form(None),
    password: str = Form(None),
    user_name: str = Form(None),
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
        
        if historical:
            try:
                # Convert string to dictionary
                data_dict = json.loads(historical)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON for historical field: {str(e)}")
        else:
            data_dict = {}

        # Create dynamic fields for the historical model
        dynamic_fields = {key: (type(value), ...) for key, value in data_dict.items()}
        DynamicModel = create_model('DynamicModel', **dynamic_fields)
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
        raise HTTPException(status_code=500, detail=str(e))
    
##GET LIST STAFF
@router.get("/staff/list")
async def view_staff(
    user: str = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")

        staffs = db.query(MedicalStaff).all()
        if not staffs:
            raise HTTPException(status_code=404, detail="No staffs found")
        return staffs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
##GET STAFF BY STAFF_ID
@router.get("/staff/{staff_id}")
async def get_staff_by_id(
    staff_id: str, 
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")
        
        staff = db.query(MedicalStaff).filter(MedicalStaff.staff_id == staff_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")
        return staff
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
@router.put("/staff/{staff_id}")
async def update_staff(
    staff_id: str,
    name: str = Form(None),
    dob: int = Form(None),  
    pob: str = Form(None),
    national_id: str = Form(None),  
    phone_num: str = Form(None),  
    tax_num: str = Form(None),  
    license_num: str = Form(None),  
    historical: Dict | str = Form(None),
    address: Optional[str] = Form(None),
    sex: bool = Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):  
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")
        
        staff = db.query(MedicalStaff).filter(MedicalStaff.staff_id == staff_id).first()
        if not staff:
            raise HTTPException(status_code=404, detail="Staff not found")

        if name is not None:
            staff.name = name
        if dob is not None:
            staff.dob = datetime.fromtimestamp(dob)
        if pob is not None:
            staff.pob = pob
        if national_id is not None:
            staff.national_id = national_id
        if phone_num is not None:
            staff.phone_num = phone_num
        if tax_num is not None:
            staff.tax_num = tax_num
        if license_num is not None:
            staff.license_num = license_num
        if historical is not None:
            try:
                data_dict = json.loads(historical)
            except json.JSONDecodeError as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON for historical field: {str(e)}")
            dynamic_fields = {key: (type(value), ...) for key, value in data_dict.items()}
            DynamicModel = create_model('DynamicModel', **dynamic_fields)
            dynamic_instance = DynamicModel(**data_dict).json()
            staff.historical = dynamic_instance
        if address is not None:
            staff.address = address
        if sex is not None:
            staff.sex = sex

        db.commit()
        db.refresh(staff)
        return staff
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


#REGISTER NEW POLYCLINIC
@router.post("/poly/new")
async def register_polyclinic(
    poly_name: str = Form(None),
    poly_desc: str = Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
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
    
##GET LIST POLYCLINIC
@router.get("/poly/list")
async def view_poly(
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        # if user.user_type != 1:
        #     raise HTTPException(status_code=403, detail="Access forbidden")

        polyclinics = db.query(Polyclinic).all()
        if not polyclinics:
            raise HTTPException(status_code=404, detail="No polyclinics found")
        return polyclinics
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
##GET POLY BY POLY_ID
@router.get("/poly/{poly_id}")
async def get_poly_by_id(
    poly_id: str, 
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")
        
        polyclinic = db.query(Polyclinic).filter(Polyclinic.poly_id == poly_id).first()
        if not polyclinic:
            raise HTTPException(status_code=404, detail="Polyclinic not found")
        return polyclinic
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
##CONTINUE HERE 06 JUNE 2024 01:18AM
#UPDATE POLYCLINIC
@router.put("/poly/{poly_id}")
async def update_polyclinic(
    poly_id: str,
    poly_name: str = Form(None),
    poly_desc: str = Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")

        polyclinic = db.query(Polyclinic).filter(Polyclinic.poly_id == poly_id).first()
        if not polyclinic:
            raise HTTPException(status_code=404, detail="Polyclinic not found")
        
        if poly_name is not None:
            polyclinic.poly_name = poly_name
        if poly_desc is not None:
            polyclinic.poly_desc = poly_desc

        db.commit()
        db.refresh(polyclinic)
        return polyclinic
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


#REGISTER NEW LABORATORY
@router.post("/lab/new")
async def register_laboratory(
    lab_name: str = Form(None),
    lab_desc: str = Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    ## Check for duplicate laboratory name
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
    
##GET LIST LAB
@router.get("/lab/list")
async def view_lab(
    user: str = Depends(get_current_user), 
    db: Session = Depends(get_db)):
    try:
        # if user.user_type != 1:
        #     raise HTTPException(status_code=403, detail="Access forbidden")

        labs = db.query(Laboratory).all()
        if not labs:
            raise HTTPException(status_code=404, detail="No labs found")
        return labs
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

##GET LAB BY LAB_ID
@router.get("/lab/{lab_id}")
async def get_lab_by_id(
    lab_id: str, 
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        # if user.user_type != 1:
        #     raise HTTPException(status_code=403, detail="Access forbidden")
    
        lab = db.query(Laboratory).filter(Laboratory.lab_id == lab_id).first()
        if not lab:
            raise HTTPException(status_code=404, detail="Laboratory not found")
        return lab
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

# UPDATE LABORATORY
@router.put("/lab/{lab_id}")
async def update_laboratory(
    lab_id: str,
    lab_name: str = Form(None),
    lab_desc: str = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")
    
        laboratory = db.query(Laboratory).filter(Laboratory.lab_id == lab_id).first()
        if not laboratory:
            raise HTTPException(status_code=404, detail="Laboratory not found")

        if lab_name is not None:
            laboratory.lab_name = lab_name
        if lab_desc is not None:
            laboratory.lab_desc = lab_desc

        db.commit()
        db.refresh(laboratory)
        return laboratory
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")


#ASSIGN DOCTOR TO POLYCLINIC
@router.post("/poly/assign-doctor")
async def register_doctor_polyclinic(
    poly_id: str=Form(None),
    doctor_id: str=Form(None),
    user: str = Depends(get_current_user),
    db=Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    ## Check if doctor_id exist
    existing_doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
    if not existing_doctor:
        raise HTTPException(status_code=400, detail="This doctor ID is missing or does not exist")
    
    ## Check if poly_id exist
    existing_poly = db.query(Polyclinic).filter(Polyclinic.poly_id == poly_id).first()
    if not existing_poly:
        raise HTTPException(status_code=400, detail="This polyclinic ID is missing or does not exist")
    
    # Check if doctor is already assigned to the same poly
    existing_assignment = db.query(PolyclinicDoctor).filter(
        PolyclinicDoctor.poly_id == poly_id, PolyclinicDoctor.doctor_id == doctor_id
    ).first()
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Doctor is already assigned to this polyclinic")
    
    try:        
        polyclinic_doctor = PolyclinicDoctor(poly_id=poly_id, doctor_id=doctor_id)
        db.add(polyclinic_doctor)
        db.commit()
        db.refresh(polyclinic_doctor)
        return polyclinic_doctor
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

#REMOVE DOCTOR FROM POLYCLINIC
@router.delete("/poly/remove-doctor")
async def remove_doctor_from_polyclinic(
    poly_id: str = Form(None),
    doctor_id: str = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        # Check if the assignment exists
        existing_assignment = db.query(PolyclinicDoctor).filter(
            PolyclinicDoctor.poly_id == poly_id, PolyclinicDoctor.doctor_id == doctor_id
        ).first()
        if not existing_assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")

        # Remove the assignment
        db.delete(existing_assignment)
        db.commit()
        return {"message": "Doctor removed from polyclinic successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")


#REGISTER/ASSIGN STAFF TO LABORATORY
@router.post("/lab/assign-staff")
async def assign_staff_laboratory(
    lab_id: str = Form(None),
    staff_id: str = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Check if staff_id exists
    existing_staff = db.query(MedicalStaff).filter(MedicalStaff.staff_id == staff_id).first()
    if not existing_staff:
        raise HTTPException(status_code=404, detail="Staff ID not found")

    # Check if lab_id exists
    existing_lab = db.query(Laboratory).filter(Laboratory.lab_id == lab_id).first()
    if not existing_lab:
        raise HTTPException(status_code=404, detail="Laboratory ID not found")

    # Check if staff is already assigned to the laboratory
    existing_assignment = db.query(LaboratoryStaff).filter(
        LaboratoryStaff.lab_id == lab_id, LaboratoryStaff.staff_id == staff_id
    ).first()
    if existing_assignment:
        raise HTTPException(status_code=400, detail="Staff is already assigned to this laboratory")

    try:
        staff_laboratory = LaboratoryStaff(staff_id=staff_id, lab_id=lab_id)
        db.add(staff_laboratory)
        db.commit()
        db.refresh(staff_laboratory)
        return staff_laboratory
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")
    
# REMOVE STAFF FROM LABORATORY
@router.delete("/lab/remove-staff")
async def remove_staff_from_laboratory(
    lab_id: str = Form(None),
    staff_id: str = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    try:
        # Check if the assignment exists
        existing_assignment = db.query(LaboratoryStaff).filter(
            LaboratoryStaff.lab_id == lab_id, LaboratoryStaff.staff_id == staff_id
        ).first()
        if not existing_assignment:
            raise HTTPException(status_code=404, detail="Assignment not found")

        # Remove the assignment
        db.delete(existing_assignment)
        db.commit()
        return {"message": "Staff removed from laboratory successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/patient/assign-interest")
async def assign_patient_interest(
    patient_id: Optional[str] = Form(None),
    staff_id: Optional[str] = Form(None),
    doctor_id: Optional[str] = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Validate input: Either staff_id or doctor_id must be provided
    if not staff_id and not doctor_id:
        raise HTTPException(status_code=400, detail="Either staff_id or doctor_id is required")

    # Check if patient exists
    existing_patient = db.query(Patient).filter(Patient.patient_id == patient_id).first()
    if not existing_patient:
        raise HTTPException(status_code=404, detail="Patient not found")

    # Check if staff exists (if provided)
    if staff_id:
        existing_staff = db.query(MedicalStaff).filter(MedicalStaff.staff_id == staff_id).first()
        if not existing_staff:
            raise HTTPException(status_code=404, detail="Staff not found")

    # Check if doctor exists (if provided)
    if doctor_id:
        existing_doctor = db.query(Doctor).filter(Doctor.doctor_id == doctor_id).first()
        if not existing_doctor:
            raise HTTPException(status_code=404, detail="Doctor not found")

    # Attempt to create patient interest record
    existing_interest = db.query(PatientInterest).filter(
        PatientInterest.patient_id == patient_id,
        (PatientInterest.staff_id == staff_id) | (PatientInterest.doctor_id == doctor_id)
    ).first()

    if existing_interest:
        raise HTTPException(status_code=400, detail="Patient interest already exists")

    try:
        patient_interest = PatientInterest(patient_id=patient_id, staff_id=staff_id, doctor_id=doctor_id)
        db.add(patient_interest)
        db.commit()
        return {"message": "Patient interest successfully assigned"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Internal server error")

# REMOVE PATIENT INTEREST
@router.delete("/patient/remove-interest")
async def remove_patient_interest(
    patient_id: str = Form(...),
    staff_id: str = Form(None),
    doctor_id: str = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 1:
        raise HTTPException(status_code=403, detail="Access forbidden")

    # Check if the patient interest record exists based on the combination of parameters
    existing_interest = db.query(PatientInterest).filter(
        PatientInterest.patient_id == patient_id,
        ((PatientInterest.staff_id == staff_id) & (PatientInterest.doctor_id == None)) |
        ((PatientInterest.doctor_id == doctor_id) & (PatientInterest.staff_id == None))
    ).first()

    if not existing_interest:
        raise HTTPException(status_code=404, detail="Patient interest not found")

    try:
        # Delete the patient interest record
        db.delete(existing_interest)
        db.commit()
        return {"message": "Patient interest successfully removed"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))

#CREATE NEW MEDICAL RECORD
@router.post("/emr/new")
async def create_medical_record(
    patient_id: Optional[str] = Form(None),
    created_date: datetime = Form(None),
    last_editted: datetime = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type not in [1,2,3]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check existing medical record
    medical_record = db.query(MedicalRecord).filter(MedicalRecord.patient_id == patient_id).first()
    if medical_record:
        raise HTTPException(status_code=400, detail="There is existing medical record") 
    
    record_id = str(uuid.uuid4())  # Generate a UUID for record
    
    try:
        medical_record = MedicalRecord(record_id=record_id, patient_id=patient_id, created_date=created_date, last_editted=last_editted)
        db.add(medical_record)
        db.commit()
        db.refresh(medical_record)
        return medical_record

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
##GET LIST MEDICAL RECORD
@router.get("/emr/list")
async def view_emr(
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        if user.user_type != 1:
            raise HTTPException(status_code=403, detail="Access forbidden")

        records = db.query(MedicalRecord).all()
        if not records:
            raise HTTPException(status_code=404, detail="No records found")
        return records
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
    
##GET MEDICAL RECORD BY ID
@router.get("/emr/{record_id}")
async def get_medical_record(
    record_id: str, 
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)):
    try:
        # if user.user_type != 1:
        #     raise HTTPException(status_code=403, detail="Access forbidden")
        
        medical_record = db.query(MedicalRecord).filter(MedicalRecord.record_id == record_id).first()
        if not medical_record:
            raise HTTPException(status_code=404, detail="Medical record not found")

        medical_record.medical_note = db.query(MedicalNote).filter(MedicalNote.record_id == record_id).all()
        medical_record.clinical_entry = db.query(ClinicalEntry).filter(ClinicalEntry.record_id == record_id).all()
        medical_record.lab_report = db.query(LabReport).filter(LabReport.record_id == record_id).all()

        return medical_record
    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

#CONTI NUE 6 JUNI 2024 05:54AM    
## CREATE NEW MEDICAL_NOTE
@router.post("/emr/new-medical-note")
async def create_medical_note(
    record_id: str = Form(None),
    note_date: int = Form(None),
    note_content: str = Form(None),
    doctor_id: str = Form(None),
    poly_id: str = Form(None),
    attachment: UploadFile = File(None),
    diagnosis: str = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 2:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check existing medical record
    medical_record = db.query(MedicalRecord).filter(MedicalRecord.record_id == record_id).first()
    if not medical_record:
        raise HTTPException(status_code=404, detail="Medical record not found") 
    
    note_id = str(uuid.uuid4())  # Generate a UUID for record

    try:
        attachment_path = None
        if attachment:
            save_dir = "attachments"
            os.makedirs(save_dir, exist_ok=True)
            file_location = f"{save_dir}/{note_id}_{attachment.filename}"
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(attachment.file, file_object)
            attachment_path = file_location

        note_date = datetime.fromtimestamp(note_date)

        medical_note = MedicalNote(
            note_id=note_id,
            record_id=record_id,
            note_date=note_date,
            note_content=note_content,
            doctor_id=doctor_id,
            poly_id=poly_id,
            attachment=attachment_path,
            diagnosis=diagnosis
        )
        db.add(medical_note)
        db.commit()
        db.refresh(medical_note)
        return medical_note

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

#UPDATE MEDICAL_NOTE
@router.put("/emr/medical-note/{note_id}")
async def update_medical_note(
    note_id: str,
    note_content: str = Form(None),
    diagnosis: str = Form(None),
    attachment: UploadFile = File(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if user.user_type != 2:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check if the medical note exists
    medical_note = db.query(MedicalNote).filter(MedicalNote.note_id == note_id).first()
    if not medical_note:
        raise HTTPException(status_code=404, detail="Medical note not found")

    try:
        # Update the medical note content and diagnosis if provided
        if note_content is not None:
            medical_note.note_content = note_content
        if diagnosis is not None:
            medical_note.diagnosis = diagnosis

        # Update the attachment if provided
        if attachment:
            save_dir = "attachments"
            os.makedirs(save_dir, exist_ok=True)
            file_location = f"{save_dir}/{note_id}_{attachment.filename}"
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(attachment.file, file_object)
            medical_note.attachment = file_location

        db.commit()
        db.refresh(medical_note)
        return medical_note

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    
## CREATE NEW CLINICAL ENTRY IN EXISTING RECORD
@router.post("/emr/new-clinical-entry") 
async def create_clinical_entry(
    record_id: str = Form(None),
    entry_date: int = Form(None),
    staff_id: str = Form(None),
    height: Optional[int] = Form(None),
    weight: Optional[int] = Form(None),
    body_temp: Optional[float] = Form(None),
    blood_type: Optional[str] = Form(None),
    systolic: Optional[int] = Form(None),
    diastolic: Optional[int] = Form(None),
    pulse: Optional[int] = Form(None),
    note: Optional[str] = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.user_type not in [1,2,3,4]:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check existing medical record
    medical_record = db.query(MedicalRecord).filter(MedicalRecord.record_id == record_id).first()
    if not medical_record:
        raise HTTPException(status_code=400, detail="Medical record not found")
    
    entry_id = str(uuid.uuid4())  # Generate a UUID for record
    
    try:
        entry_date = datetime.fromtimestamp(entry_date)

        clinical_entry = ClinicalEntry(
            entry_id=entry_id,
            record_id=record_id,
            entry_date=entry_date,
            staff_id=staff_id,
            height=height,
            weight=weight,
            body_temp=body_temp,
            blood_type=blood_type,
            systolic=systolic,
            diastolic=diastolic,
            pulse=pulse,
            note=note
        )
        db.add(clinical_entry)
        db.commit()
        db.refresh(clinical_entry)
        return clinical_entry

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
#UPDATE CLINICAL ENTRY
@router.put("/emr/clinical-entry/{entry_id}")
async def update_clinical_entry(
    entry_id: str,
    height: Optional[int] = Form(None),
    weight: Optional[int] = Form(None),
    body_temp: Optional[float] = Form(None),
    blood_type: Optional[str] = Form(None),
    systolic: Optional[int] = Form(None),
    diastolic: Optional[int] = Form(None),
    pulse: Optional[int] = Form(None),
    note: Optional[str] = Form(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.user_type != 3:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check if the clinical entry exists
    clinical_entry = db.query(ClinicalEntry).filter(ClinicalEntry.entry_id == entry_id).first()
    if not clinical_entry:
        raise HTTPException(status_code=404, detail="Clinical entry not found")

    try:
        # Update the clinical entry details if provided
        if height is not None:
            clinical_entry.height = height
        if weight is not None:
            clinical_entry.weight = weight
        if body_temp is not None:
            clinical_entry.body_temp = body_temp
        if blood_type is not None:
            clinical_entry.blood_type = blood_type
        if systolic is not None:
            clinical_entry.systolic = systolic
        if diastolic is not None:
            clinical_entry.diastolic = diastolic
        if pulse is not None:
            clinical_entry.pulse = pulse
        if note is not None:
            clinical_entry.note = note

        db.commit()
        db.refresh(clinical_entry)
        return clinical_entry

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


## CREATE NEW LAB REPORT IN EXISTING RECORD
@router.post("/emr/new-lab-report") 
async def create_lab_report(
    record_id: str = Form(None),
    report_date: int = Form(None),
    lab_note: str = Form(None),
    staff_id: str = Form(None),
    lab_id: str = Form(None),
    attachment: Optional[UploadFile] = File(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.user_type != 3:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check existing medical record
    medical_record = db.query(MedicalRecord).filter(MedicalRecord.record_id == record_id).first()
    if not medical_record:
        raise HTTPException(status_code=400, detail="Medical record not found")
    
    report_id = str(uuid.uuid4())  # Generate a UUID for record

    try:
        report_date = datetime.fromtimestamp(report_date)

        attachment_path = None
        if attachment:
            save_dir = "attachments"
            os.makedirs(save_dir, exist_ok=True)
            file_location = f"{save_dir}/{record_id}_{attachment.filename}"
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(attachment.file, file_object)
            attachment_path = file_location

        lab_report = LabReport(
            report_id = report_id,
            record_id=record_id,
            report_date=report_date,
            lab_note=lab_note,
            staff_id=staff_id,
            lab_id=lab_id,
            attachment=attachment_path,
        )
        db.add(lab_report)
        db.commit()
        db.refresh(lab_report)
        return lab_report

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")

@router.put("/emr/update-lab-report/{report_id}")
async def update_lab_report(
    report_id: str,
    lab_note: str = Form(None),
    staff_id: str = Form(None),
    lab_id: str = Form(None),
    attachment: Optional[UploadFile] = File(None),
    user: str = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if user.user_type != 3:
        raise HTTPException(status_code=403, detail="Access forbidden")
    
    # Check if the lab report exists
    lab_report = db.query(LabReport).filter(LabReport.report_id == report_id).first()
    if not lab_report:
        raise HTTPException(status_code=404, detail="Lab report not found")

    try:
        # Update the lab report details if provided
        if lab_note is not None:
            lab_report.lab_note = lab_note
        if staff_id is not None:
            lab_report.staff_id = staff_id
        if lab_id is not None:
            lab_report.lab_id = lab_id
        if attachment is not None:
            # Save attachment if provided
            save_dir = "attachments"
            os.makedirs(save_dir, exist_ok=True)
            file_location = f"{save_dir}/{report_id}_{attachment.filename}"
            with open(file_location, "wb") as file_object:
                shutil.copyfileobj(attachment.file, file_object)
            lab_report.attachment = file_location

        db.commit()
        db.refresh(lab_report)
        return lab_report

    except Exception as e:
        raise HTTPException(status_code=500, detail="Internal server error")
