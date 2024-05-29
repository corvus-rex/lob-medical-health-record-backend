from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB ,UUID
from sqlalchemy.orm import relationship
from sqlalchemy import Date


Base = declarative_base()

class User(Base):
    __tablename__ = 'user'
    user_id = Column(UUID, primary_key=True, index=True)
    user_name = Column(String)
    user_type = Column(Integer)
    user_email = Column(String, index=True)
    password = Column(String)

    patient = relationship("Patient", back_populates="user")
    admin = relationship("Admin", back_populates="user")
    doctor = relationship("Doctor", back_populates="user")
    medical_staff = relationship("MedicalStaff", back_populates="user")

class Patient(Base):
    __tablename__ = 'patient'
    patient_id = Column(UUID, primary_key=True, index=True)
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

    user = relationship("User", back_populates="patient")
    insurance = relationship("Insurance", back_populates="patient")
    medical_record = relationship("MedicalRecord", back_populates="patient")
    interest = relationship("PatientInterest", back_populates="patient")

class Admin(Base):
    __tablename__ = 'admin'
    admin_id = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey('user.user_id'))
    name = Column(String)
    dob = Column(DateTime)
    national_id = Column(Integer)
    tax_number = Column(Integer)
    sex = Column(Boolean)
    phone_num = Column(Integer)
    address = Column(String)

    user = relationship("User", back_populates="admin")

class Insurance(Base):
    __tablename__ = 'insurance'
    insurance_id = Column(UUID, primary_key=True, index=True)
    insurance_name = Column(String)

    patient = relationship("Patient", back_populates="insurance")

class Doctor(Base):
    __tablename__ = 'doctor'
    doctor_id = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey('user.user_id'))
    name = Column(String, nullable=False)
    dob = Column(DateTime, nullable=False)
    national_id = Column(Integer)
    phone_num = Column(Integer, nullable=False)
    address = Column(String)
    pob = Column(String, nullable=False)
    license_num = Column(String, nullable=False)
    tax_num = Column(Integer, nullable=False)
    historical = Column(JSONB, nullable=False)
    sex = Column(Boolean)

    user = relationship("User", back_populates="doctor")
    polyclinic = relationship("PolyclinicDoctor", back_populates="doctor")
    medical_note = relationship("MedicalNote", back_populates="doctor")
    interest = relationship("PatientInterest", back_populates="doctor")

class MedicalStaff(Base):
    __tablename__ = 'medical_staff'
    staff_id = Column(UUID, primary_key=True, index=True)
    user_id = Column(UUID, ForeignKey('user.user_id'))
    name = Column(String, nullable=False)
    dob = Column(DateTime, nullable=False)
    national_id = Column(Integer)
    phone_num = Column(Integer, nullable=False)
    address = Column(String)
    pob = Column(String, nullable=False)
    license_num = Column(String, nullable=False)
    tax_num = Column(Integer, nullable=False)
    historical = Column(JSONB, nullable=False)
    sex = Column(Boolean)

    user = relationship("User", back_populates="medical_staff")
    lab_report = relationship("LabReport", back_populates="staff")
    clinical_entrie = relationship("ClinicalEntry", back_populates="staff")
    interest = relationship("PatientInterest", back_populates="staff")
    laboratory_staff = relationship("LaboratoryStaff", back_populates="staff")

class Laboratory(Base):
    __tablename__ = 'laboratory'
    lab_id = Column(UUID, primary_key=True, index=True)
    lab_name = Column(String, nullable=False)
    lab_desc = Column(String)

    staff = relationship("LaboratoryStaff", back_populates="lab")
    lab_report = relationship("LabReport", back_populates="lab")

class Polyclinic(Base):
    __tablename__ = 'polyclinic'
    poly_id = Column(UUID, primary_key=True, index=True)
    poly_name = Column(String, nullable=False)
    poly_desc = Column(String)

    doctor = relationship("PolyclinicDoctor", back_populates="polyclinic")
    medical_note = relationship("MedicalNote", back_populates="polyclinic")

class PolyclinicDoctor(Base):
    __tablename__ = 'polyclinic_doctor'
    doctor_id = Column(UUID, ForeignKey('doctor.doctor_id'), primary_key=True)
    poly_id = Column(UUID, ForeignKey('polyclinic.poly_id'), primary_key=True)

    doctor = relationship("Doctor", back_populates="polyclinic")
    polyclinic = relationship("Polyclinic", back_populates="doctor")

class LaboratoryStaff(Base):
    __tablename__ = 'laboratory_staff'
    staff_id = Column(UUID, ForeignKey('medical_staff.staff_id'), primary_key=True)
    lab_id = Column(UUID, ForeignKey('laboratory.lab_id'), primary_key=True)

    staff = relationship("MedicalStaff", back_populates="laboratory_staff")
    lab = relationship("Laboratory", back_populates="staff")

class PatientInterest(Base):
    __tablename__ = 'patient_interest'
    patient_id = Column(UUID, ForeignKey('patient.patient_id'), primary_key=True)
    doctor_id = Column(UUID, ForeignKey('doctor.doctor_id'), primary_key=True)
    staff_id = Column(UUID, ForeignKey('medical_staff.staff_id'), primary_key=True)

    patient = relationship("Patient", back_populates="interest")
    doctor = relationship("Doctor", back_populates="interest")
    staff = relationship("MedicalStaff", back_populates="interest")

class MedicalRecord(Base):
    __tablename__ = 'medical_record'
    record_id = Column(UUID, primary_key=True, index=True)
    patient_id = Column(UUID, ForeignKey('patient.patient_id'), nullable=False)
    created_date = Column(DateTime(timezone=True), nullable=False)
    last_edited = Column(DateTime(timezone=True), nullable=False)

    patient = relationship("Patient", back_populates="medical_record")
    clinical_entry = relationship("ClinicalEntry", back_populates="record")
    medical_note = relationship("MedicalNote", back_populates="record")
    lab_report = relationship("LabReport", back_populates="record")

class ClinicalEntry(Base):
    __tablename__ = 'clinical_entry'
    entry_id = Column(UUID, primary_key=True, index=True)
    record_id = Column(UUID, ForeignKey('medical_record.record_id'), nullable=False)
    entry_date = Column(Date, nullable=False)
    staff_id = Column(UUID, ForeignKey('medical_staff.staff_id'), nullable=False)
    height = Column(Integer)
    weight = Column(Integer)
    body_temp = Column(Float)
    blood_type = Column(String(3))
    systolic = Column(Integer)
    diastolic = Column(Integer)
    pulse = Column(Integer)
    note = Column(String)

    record = relationship("MedicalRecord", back_populates="clinical_entry")
    staff = relationship("MedicalStaff", back_populates="clinical_entry")

class MedicalNote(Base):
    __tablename__ = 'medical_note'
    note_id = Column(UUID, primary_key=True, index=True)
    record_id = Column(UUID, ForeignKey('medical_record.record_id'), nullable=False)
    note_date = Column(Date, nullable=False)
    note_content = Column(String, nullable=False)
    doctor_id = Column(UUID, ForeignKey('doctor.doctor_id'), nullable=False)
    poly_id = Column(UUID, ForeignKey('polyclinic.poly_id'), nullable=False)
    attachment = Column(String)
    diagnosis = Column(String, nullable=False)

    record = relationship("MedicalRecord", back_populates="medical_note")
    doctor = relationship("Doctor", back_populates="medical_note")
    polyclinic = relationship("Polyclinic", back_populates="medical_note")

class LabReport(Base):
    __tablename__ = 'lab_report'
    report_id = Column(UUID, primary_key=True, index=True)
    record_id = Column(UUID, ForeignKey('medical_record.record_id'), nullable=False)
    report_date = Column(Date, nullable=False)
    lab_note = Column(String, nullable=False)
    staff_id = Column(UUID, ForeignKey('medical_staff.staff_id'), nullable=False)
    lab_id = Column(UUID, ForeignKey('laboratory.lab_id'), nullable=False)
    attachment = Column(String)

    record = relationship("MedicalRecord", back_populates="lab_report")
    staff = relationship("MedicalStaff", back_populates="lab_report")
    lab = relationship("Laboratory", back_populates="lab_report")