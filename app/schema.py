from pydantic import BaseModel
from datetime import datetime, date
from typing import Dict, Optional

class User(BaseModel):
    user_id: str
    user_name: str
    user_type: int
    user_email: str
    password: str
    class Config:
        orm_mode = True

class Admin(BaseModel):
    admin_id: str
    user_id: str
    name: str
    dob: datetime
    tax_number: int
    national_id: int
    sex: bool
    phone_num: Optional[int]
    address: Optional[str]
    class Config:
        orm_mode = True

class Patient(BaseModel):
    patient_id: str
    user_id: str
    name: str
    dob: datetime
    national_id: str
    sex: bool
    phone_num: str
    address: Optional[str]
    alias: Optional[str]
    relative_phone: str
    insurance_id: Optional[str]
    class Config:
        orm_mode = True

class Insurance(BaseModel):
    insurance_id: str
    insurance_name: str
    class Config:
        orm_mode = True

class Doctor(BaseModel):
    doctor_id: str
    user_id: str
    name: str
    dob: datetime
    national_id: int
    phone_num: int
    address: Optional[str]
    pob: str
    license_num: str
    tax_num: int
    historical: Dict
    sex: bool

    class Config:
        orm_mode = True

class MedicalStaff(BaseModel):
    staff_id: str
    user_id: str
    name: str
    dob: datetime
    national_id: int
    phone_num: int
    address: Optional[str]
    pob: str
    license_num: str
    tax_num: int
    historical: Dict
    sex: bool

    class Config:
        orm_mode = True

class Laboratory(BaseModel):
    lab_id: str
    lab_name: str
    lab_desc: Optional[str]

    class Config:
        orm_mode = True

class Polyclinic(BaseModel):
    poly_id: str
    poly_name: str
    poly_desc: Optional[str]

    class Config:
        orm_mode = True

class PolyclinicDoctor(BaseModel):
    doctor_id: str
    poly_id: str

    class Config:
        orm_mode = True

class LaboratoryStaff(BaseModel):
    staff_id: str
    lab_id: str

    class Config:
        orm_mode = True

class PatientInterest(BaseModel):
    patient_id: str
    doctor_id: str
    staff_id: str

    class Config:
        orm_mode = True

class MedicalRecord(BaseModel):
    record_id: str
    patient_id: str
    created_date: datetime
    last_editted: datetime

    class Config:
        orm_mode = True

class ClinicalEntry(BaseModel):
    entry_id: str
    record_id: str
    entry_date: date
    staff_id: str
    height: Optional[int]
    weight: Optional[int]
    body_temp: Optional[float]
    blood_type: Optional[str]
    systolic: Optional[int]
    diastolic: Optional[int]
    pulse: Optional[int]
    note: Optional[str]

    class Config:
        orm_mode = True

class MedicalNote(BaseModel):
    note_id: str
    record_id: str
    note_date: date
    note_content: str
    doctor_id: str
    poly_id: str
    attachment: Optional[str]
    diagnosis: str

    class Config:
        orm_mode = True

class LabReport(BaseModel):
    report_id: str
    record_id: str
    report_date: date
    lab_note: str
    staff_id: str
    lab_id: str
    attachment: str

    class Config:
        orm_mode = True
