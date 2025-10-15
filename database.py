# database.py
from models import Session, Patient, Doctor, Treatment, TreatmentPercentage, Appointment, Payment
import datetime
import os

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

# Similar CRUD functions for doctors, treatments, appointments, payments...
# For brevity, implement similarly based on the patient functions.

# More complex example with treatment percentages:
def add_treatment_percentage(treatment_id, doctor_id, clinic_percentage, doctor_percentage):
    session = Session()
    perc = TreatmentPercentage(treatment_id=treatment_id, doctor_id=doctor_id,
                               clinic_percentage=clinic_percentage, doctor_percentage=doctor_percentage)
    session.add(perc)
    session.commit()
    session.close()

def calculate_shares(appointment_id, total_amount, discounts=0, taxes=0):
    session = Session()
    appointment = session.query(Appointment).get(appointment_id)
    perc = session.query(TreatmentPercentage).filter_by(treatment_id=appointment.treatment_id,
                                                        doctor_id=appointment.doctor_id).first()
    if perc:
        clinic_perc = perc.clinic_percentage
        doctor_perc = perc.doctor_percentage
    else:
        clinic_perc = 50.0
        doctor_perc = 50.0
    net_amount = total_amount - discounts + taxes
    clinic_share = net_amount * clinic_perc / 100
    doctor_share = net_amount * doctor_perc / 100
    session.close()
    return clinic_share, doctor_share
