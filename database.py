# database.py
from models import Session, Patient, Doctor, Treatment, TreatmentPercentage, Appointment, Payment
import datetime
import os

# --- Patient CRUD ---

def add_patient(name, age, gender, phone, address, medical_history, image=None):
    session = Session()
    patient = Patient(name=name, age=age, gender=gender, phone=phone, address=address, medical_history=medical_history)
    if image:
        os.makedirs("images", exist_ok=True)
        image_path = f"images/{name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
        with open(image_path, 'wb') as f:
            f.write(image.getvalue())
        patient.image_path = image_path
    session.add(patient)
    session.commit()
    session.close()

def edit_patient(patient_id, name, age, gender, phone, address, medical_history, image=None):
    session = Session()
    patient = session.query(Patient).get(patient_id)
    if patient:
        patient.name = name
        patient.age = age
        patient.gender = gender
        patient.phone = phone
        patient.address = address
        patient.medical_history = medical_history
        if image:
            os.makedirs("images", exist_ok=True)
            image_path = f"images/{name}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.png"
            with open(image_path, 'wb') as f:
                f.write(image.getvalue())
            patient.image_path = image_path
        session.commit()
    session.close()

def delete_patient(patient_id):
    session = Session()
    patient = session.query(Patient).get(patient_id)
    if patient:
        session.delete(patient)
        session.commit()
    session.close()

def get_patients():
    session = Session()
    patients = session.query(Patient).all()
    session.close()
    return patients

# --- Doctor CRUD ---

def add_doctor(name, specialty, phone, email):
    session = Session()
    doctor = Doctor(name=name, specialty=specialty, phone=phone, email=email)
    session.add(doctor)
    session.commit()
    session.close()

def edit_doctor(doctor_id, name, specialty, phone, email):
    session = Session()
    doctor = session.query(Doctor).get(doctor_id)
    if doctor:
        doctor.name = name
        doctor.specialty = specialty
        doctor.phone = phone
        doctor.email = email
        session.commit()
    session.close()

def delete_doctor(doctor_id):
    session = Session()
    doctor = session.query(Doctor).get(doctor_id)
    if doctor:
        session.delete(doctor)
        session.commit()
    session.close()

def get_doctors():
    session = Session()
    doctors = session.query(Doctor).all()
    session.close()
    return doctors

# --- Treatment CRUD ---

def add_treatment(name, base_cost):
    session = Session()
    treatment = Treatment(name=name, base_cost=base_cost)
    session.add(treatment)
    session.commit()
    session.close()

def edit_treatment(treatment_id, name, base_cost):
    session = Session()
    treatment = session.query(Treatment).get(treatment_id)
    if treatment:
        treatment.name = name
        treatment.base_cost = base_cost
        session.commit()
    session.close()

def delete_treatment(treatment_id):
    session = Session()
    treatment = session.query(Treatment).get(treatment_id)
    if treatment:
        session.delete(treatment)
        session.commit()
    session.close()

def get_treatments():
    session = Session()
    treatments = session.query(Treatment).all()
    session.close()
    return treatments

# --- Treatment Percentage CRUD ---

def add_treatment_percentage(treatment_id, doctor_id, clinic_percentage, doctor_percentage):
    session = Session()
    perc = TreatmentPercentage(treatment_id=treatment_id, doctor_id=doctor_id,
                               clinic_percentage=clinic_percentage, doctor_percentage=doctor_percentage)
    session.add(perc)
    session.commit()
    session.close()

# --- Appointment CRUD ---

def add_appointment(patient_id, doctor_id, treatment_id, date, status, notes):
    session = Session()
    appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, treatment_id=treatment_id,
                              date=date, status=status, notes=notes)
    session.add(appointment)
    session.commit()
    session.close()

def edit_appointment(appointment_id, patient_id, doctor_id, treatment_id, date, status, notes):
    session = Session()
    appointment = session.query(Appointment).get(appointment_id)
    if appointment:
        appointment.patient_id = patient_id
        appointment.doctor_id = doctor_id
        appointment.treatment_id = treatment_id
        appointment.date = date
        appointment.status = status
        appointment.notes = notes
        session.commit()
    session.close()

def delete_appointment(appointment_id):
    session = Session()
    appointment = session.query(Appointment).get(appointment_id)
    if appointment:
        session.delete(appointment)
        session.commit()
    session.close()

def get_appointments():
    session = Session()
    appointments = session.query(Appointment).all()
    session.close()
    return appointments

# --- Payment and Shares ---

def calculate_shares(appointment_id, total_amount, discounts=0, taxes=0):
    session = Session()
    appointment = session.query(Appointment).get(appointment_id)
    perc = session.query(TreatmentPercentage).filter_by(
        treatment_id=appointment.treatment_id,
        doctor_id=appointment.doctor_id).first()
    if perc:
        clinic_perc = perc.clinic_percentage
        doctor_perc = perc.doctor_percentage
    else:
        clinic_perc = 50.0
        doctor_perc = 50.0
    net_amount = total_amount - discounts + taxes
    clinic_share = net_amount * (clinic_perc / 100)
    doctor_share = net_amount * (doctor_perc / 100)
    session.close()
    return clinic_share, doctor_share

def add_payment(appointment_id, total_amount, paid_amount, payment_method, discounts=0.0, taxes=0.0):
    session = Session()
    clinic_share, doctor_share = calculate_shares(appointment_id, total_amount, discounts, taxes)
    payment = Payment(
        appointment_id=appointment_id,
        total_amount=total_amount,
        paid_amount=paid_amount,
        clinic_share=clinic_share,
        doctor_share=doctor_share,
        payment_method=payment_method,
        discounts=discounts,
        taxes=taxes,
        date_paid=datetime.datetime.now()
    )
    session.add(payment)
    session.commit()
    session.close()

def get_payments():
    session = Session()
    payments = session.query(Payment).all()
    session.close()
    return payments
