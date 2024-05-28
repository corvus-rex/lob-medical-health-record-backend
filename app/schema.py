from pydantic import BaseModel
from datetime import datetime
from typing import Dict, Optional

class User(BaseModel):
    user_id: str
    user_name: str
    user_type: int
    user_email: str
    password: str
    class Config:
        orm_mode = True

class Patient(BaseModel):
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
    patient_id: str
    user_id: str
    name: str
    dob: datetime
    national_id: int
    sex: bool
    phone_num: Optional[int]
    address: Optional[str]
    alias: Optional[str]
    relative_phone: Optional[int]
    insurance_id: Optional[str]
    class Config:
        orm_mode = True

class Insurance(BaseModel):
    insurance_id: str
    insurance_name: str
    class Config:
        orm_mode = True
