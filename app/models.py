from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB, insert ,UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

Base  = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id  = Column(UUID, primary_key=True, index=True)
    user_name = Column(String)
    user_type = Column(Integer)
    user_email = Column(String, index=True)
    password = Column(String)  

class Patient(Base):
    __tablename__ = 'patient'
    patient_id  = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey('user.user_id'))
    name = Column(String)
    dob = Column(DateTime)
    national_id = Column(Integer)
    sex = Column(Boolean)
    phone_num = Column(Integer)
    address = Column(String)
    alias = Column(String)
    relative_phone = Column(Integer)
    insurance_id = Column(UUID, ForeignKey('insurance.insurance_id'))

    patient = relationship("User")
    insurance = relationship("Insurance")

class Admin(Base):
    __tablename__ = 'admin'
    admin_id  = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey('user.user_id'))
    name = Column(String)
    dob = Column(DateTime)
    national_id = Column(Integer)
    tax_number = Column(Integer)
    sex = Column(Boolean)
    phone_num = Column(Integer)
    address = Column(String)

    admin = relationship("User")

class Insurance(Base):
    __tablename__ = 'insurance'
    insurance_id = Column(UUID, primary_key=True, index=True)
    insurance_name = Column(String)