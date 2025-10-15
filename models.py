# models.py
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker

DATABASE_URL = 'sqlite:///dental_clinic.db'

engine = create_engine(DATABASE_URL, echo=True)
Session = sessionmaker(bind=engine)
Base = declarative_base()

class Patient(Base):
    __tablename__ = 'patients'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)
    gender = Column(String)
    phone = Column(String)
    address = Column(String)
    medical_history = Column(Text)
    image_path = Column(String)

class Doctor(Base):
    __tablename__ = 'doctors'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    specialty = Column(String)
    phone = Column(String)
    email = Column(String)

class Treatment(Base):
    __tablename__ = 'treatments'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    base_cost = Column(Float)

class TreatmentPercentage(Base):
    __tablename__ = 'treatment_percentages'
    id = Column(Integer, primary_key=True)
    treatment_id = Column(Integer, ForeignKey('treatments.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    clinic_percentage = Column(Float)
    doctor_percentage = Column(Float)
    treatment = relationship("Treatment")
    doctor = relationship("Doctor")

class Appointment(Base):
    __tablename__ = 'appointments'
    id = Column(Integer, primary_key=True)
    patient_id = Column(Integer, ForeignKey('patients.id'))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    treatment_id = Column(Integer, ForeignKey('treatments.id'))
    date = Column(DateTime)
    status = Column(String)
    notes = Column(Text)
    patient = relationship("Patient")
    doctor = relationship("Doctor")
    treatment = relationship("Treatment")

class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    appointment_id = Column(Integer, ForeignKey('appointments.id'))
    total_amount = Column(Float)
    paid_amount = Column(Float)
    clinic_share = Column(Float)
    doctor_share = Column(Float)
    payment_method = Column(String)
    discounts = Column(Float)
    taxes = Column(Float)
    date_paid = Column(DateTime)
    appointment = relationship("Appointment")

def init_db():
    Base.metadata.create_all(engine)
