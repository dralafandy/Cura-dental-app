# dental_clinic_app.py
import streamlit as st
import pandas as pd
import datetime
import os
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import plotly.express as px
import streamlit_javascript as st_js

# Database & ORM setup
engine = create_engine('sqlite:///dental_clinic.db', echo=False)
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

class Expense(Base):
    __tablename__ = 'expenses'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    amount = Column(Float)
    date = Column(DateTime)

class InventoryItem(Base):
    __tablename__ = 'inventory_items'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    quantity = Column(Float)
    unit = Column(String)
    cost_per_unit = Column(Float)

Base.metadata.create_all(engine)

##### Utility functions #####
def get_screen_width():
    width = st_js.st_javascript("window.innerWidth")
    return width if width else 800

def determine_num_columns(width):
    if width < 600:
        return 1
    elif width < 1000:
        return 2
    else:
        return 3

##### CRUD Functions (Patients, Doctors, Treatments, etc.) #####

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

def get_patients():
    session = Session()
    patients = session.query(Patient).all()
    session.close()
    return patients

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

# Similar CRUD for doctors
def add_doctor(name, specialty, phone, email):
    session = Session()
    doctor = Doctor(name=name, specialty=specialty, phone=phone, email=email)
    session.add(doctor)
    session.commit()
    session.close()

def get_doctors():
    session = Session()
    doctors = session.query(Doctor).all()
    session.close()
    return doctors

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

# Similar CRUD for treatments
def add_treatment(name, base_cost):
    session = Session()
    treatment = Treatment(name=name, base_cost=base_cost)
    session.add(treatment)
    session.commit()
    session.close()

def get_treatments():
    session = Session()
    treatments = session.query(Treatment).all()
    session.close()
    return treatments

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

# Treatment percentages (clinic/doctor split)
def add_treatment_percentage(treatment_id, doctor_id, clinic_percentage, doctor_percentage):
    session = Session()
    perc = TreatmentPercentage(treatment_id=treatment_id, doctor_id=doctor_id,
                               clinic_percentage=clinic_percentage, doctor_percentage=doctor_percentage)
    session.add(perc)
    session.commit()
    session.close()

# Appointments CRUD
def add_appointment(patient_id, doctor_id, treatment_id, date, status, notes):
    session = Session()
    appointment = Appointment(patient_id=patient_id, doctor_id=doctor_id, treatment_id=treatment_id,
                              date=date, status=status, notes=notes)
    session.add(appointment)
    session.commit()
    session.close()

def get_appointments():
    session = Session()
    appointments = session.query(Appointment).all()
    session.close()
    return appointments

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

# Payments and financial calculations
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
    clinic_share = net_amount * clinic_perc / 100
    doctor_share = net_amount * doctor_perc / 100
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

# Expenses CRUD for clinic costs
def add_expense(description, amount, date=None):
    session = Session()
    if date is None:
        date = datetime.datetime.now()
    expense = Expense(description=description, amount=amount, date=date)
    session.add(expense)
    session.commit()
    session.close()

def get_expenses():
    session = Session()
    expenses = session.query(Expense).all()
    session.close()
    return expenses

# Inventory CRUD
def add_inventory_item(name, quantity, unit, cost_per_unit):
    session = Session()
    item = InventoryItem(name=name, quantity=quantity, unit=unit, cost_per_unit=cost_per_unit)
    session.add(item)
    session.commit()
    session.close()

def get_inventory_items():
    session = Session()
    items = session.query(InventoryItem).all()
    session.close()
    return items

def edit_inventory_item(item_id, name, quantity, unit, cost_per_unit):
    session = Session()
    item = session.query(InventoryItem).get(item_id)
    if item:
        item.name = name
        item.quantity = quantity
        item.unit = unit
        item.cost_per_unit = cost_per_unit
        session.commit()
    session.close()

def delete_inventory_item(item_id):
    session = Session()
    item = session.query(InventoryItem).get(item_id)
    if item:
        session.delete(item)
        session.commit()
    session.close()

# Financial summaries
def get_total_expenses(start_date=None, end_date=None):
    session = Session()
    query = session.query(Expense)
    if start_date and end_date:
        query = query.filter(Expense.date.between(start_date, end_date))
    total = sum(e.amount for e in query.all())
    session.close()
    return total

def get_total_revenue(start_date=None, end_date=None):
    session = Session()
    query = session.query(Payment)
    if start_date and end_date:
        query = query.filter(Payment.date_paid.between(start_date, end_date))
    total = sum(p.paid_amount for p in query.all())
    session.close()
    return total

def get_net_profit(start_date=None, end_date=None):
    return get_total_revenue(start_date, end_date) - get_total_expenses(start_date, end_date)

# Patient account details
def get_patient_payments(patient_id):
    session = Session()
    payments = session.query(Payment).join(Appointment).filter(Appointment.patient_id==patient_id).all()
    session.close()
    return payments

def get_patient_balance(patient_id):
    session = Session()
    appointments = session.query(Appointment).filter_by(patient_id=patient_id).all()
    total_due = 0
    for app in appointments:
        payments = session.query(Payment).filter_by(appointment_id=app.id).all()
        paid = sum(p.paid_amount for p in payments)
        cost = 0
        if app.treatment is not None:
            cost = app.treatment.base_cost
        total_due += max(cost - paid, 0)
    session.close()
    return total_due

# Reporting functions
def generate_report(start_date, end_date):
    session = Session()
    payments = session.query(Payment).filter(
        Payment.date_paid.between(start_date, end_date)).all()
    data = [{'موعد': p.appointment_id, 'إجمالي': p.total_amount,
             'نصيب العيادة': p.clinic_share, 'نصيب الطبيب': p.doctor_share, 'تاريخ': p.date_paid} for p in payments]
    df = pd.DataFrame(data)
    session.close()
    return df

def export_to_pdf(df):
    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    c.drawString(100, 750, "تقرير المحاسبة")
    y = 700
    x_positions = [100, 200, 300, 400, 500]
    for i, col in enumerate(df.columns):
        c.drawString(x_positions[i], y, col)
    y -= 20
    for _, row in df.iterrows():
        for i, val in enumerate(row):
            c.drawString(x_positions[i], y, str(val))
        y -= 20
        if y < 50:
            c.showPage()
            y = 750
    c.save()
    buffer.seek(0)
    return buffer

def export_to_excel(df):
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    buffer.seek(0)
    return buffer


# --- UI pages ---
def patients_page(num_cols):
    st.title("إدارة المرضى 👥")
    with st.expander("إضافة مريض جديد ➕", expanded=True):
        with st.form("add_patient"):
            cols = st.columns(num_cols)
            with cols[0]:
                name = st.text_input("الاسم")
                age = st.number_input("العمر", min_value=0)
            if num_cols > 1:
                with cols[1]:
                    gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
                    phone = st.text_input("الهاتف")
            if num_cols > 2:
                with cols[2]:
                    address = st.text_input("العنوان")
            medical_history = st.text_area("التاريخ الطبي")
            image = st.file_uploader("رفع صورة (أشعة أسنان)", type=["png", "jpg"])
            if st.form_submit_button("إضافة"):
                if not name:
                    st.error("الرجاء إدخال اسم المريض")
                else:
                    add_patient(name, age, gender, phone, address, medical_history, image)
                    st.success("تم إضافة المريض ✅")

    patients = get_patients()
    df = pd.DataFrame([{
        'id': p.id, 'name': p.name, 'age': p.age,
        'gender': p.gender, 'phone': p.phone, 'address': p.address
    } for p in patients])

    search_term = st.text_input("بحث عن مريض 🔍")
    if search_term:
        df = df[df.apply(lambda r: search_term.lower() in ' '.join(map(str,r)), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف مريض ✏️🗑️"):
        patient_id = st.number_input("معرف المريض للتعديل/الحذف", min_value=1)
        patient = next((p for p in patients if p.id == patient_id), None)
        if patient:
            with st.form("edit_patient"):
                name = st.text_input("الاسم", patient.name)
                age = st.number_input("العمر", value=patient.age, min_value=0)
                gender = st.selectbox("الجنس", ["ذكر", "أنثى"], index=0 if patient.gender == "ذكر" else 1)
                phone = st.text_input("الهاتف", patient.phone)
                address = st.text_input("العنوان", patient.address)
                medical_history = st.text_area("التاريخ الطبي", patient.medical_history)
                image = st.file_uploader("رفع صورة جديدة", type=["png", "jpg"])
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("تعديل"):
                        edit_patient(patient_id, name, age, gender, phone, address, medical_history, image)
                        st.success("تم التعديل ✅")
                with col2:
                    if st.form_submit_button("حذف"):
                        delete_patient(patient_id)
                        st.success("تم الحذف ✅")
        else:
            st.info("الرجاء إدخال معرف مريض صحيح")

def doctors_page(num_cols):
    st.title("إدارة الأطباء 👨‍⚕️")
    with st.expander("إضافة طبيب جديد ➕", expanded=True):
        with st.form("add_doctor"):
            cols = st.columns(num_cols)
            with cols[0]:
                name = st.text_input("الاسم")
                specialty = st.text_input("التخصص")
            if num_cols > 1:
                with cols[1]:
                    phone = st.text_input("الهاتف")
                    email = st.text_input("البريد الإلكتروني")
            if st.form_submit_button("إضافة"):
                if not name:
                    st.error("الرجاء إدخال اسم الطبيب")
                else:
                    add_doctor(name, specialty, phone, email)
                    st.success("تم إضافة الطبيب ✅")

    doctors = get_doctors()
    df = pd.DataFrame([{
        'id': d.id, 'name': d.name, 'specialty': d.specialty,
        'phone': d.phone, 'email': d.email
    } for d in doctors])

    search_term = st.text_input("بحث عن طبيب 🔍")
    if search_term:
        df = df[df.apply(lambda r: search_term.lower() in ' '.join(map(str, r)), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف طبيب ✏️🗑️"):
        doctor_id = st.number_input("معرف الطبيب", min_value=1)
        doctor = next((d for d in doctors if d.id == doctor_id), None)
        if doctor:
            with st.form("edit_doctor"):
                name = st.text_input("الاسم", doctor.name)
                specialty = st.text_input("التخصص", doctor.specialty)
                phone = st.text_input("الهاتف", doctor.phone)
                email = st.text_input("البريد الإلكتروني", doctor.email)
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("تعديل"):
                        edit_doctor(doctor_id, name, specialty, phone, email)
                        st.success("تم التعديل ✅")
                with col2:
                    if st.form_submit_button("حذف"):
                        delete_doctor(doctor_id)
                        st.success("تم الحذف ✅")
        else:
            st.info("الرجاء إدخال معرف طبيب صحيح")

# ... [نفس النمط لباقي الصفحات: العلاجات، المواعيد، المحاسبة، المخزون، حسابات المرضى، التقارير]

# Main app
def main():
    st.set_page_config(layout="wide", page_title="إدارة عيادة الأسنان 🦷", page_icon="🦷")
    st.markdown("""
    <style>
    html, body, [class*="css"]  {
        text-align: right; direction: rtl; font-family: 'Arial', sans-serif;
    }
    .stButton > button { width: 100%; border-radius: 8px;}
    .stDataFrame {width: 100%;}
    @media (max-width: 768px) {
        .st-expander { width: 100%; }
        .st-columns > div { flex-direction: column; }
    }
    </style>
    """, unsafe_allow_html=True)

    width = get_screen_width()
    num_cols = determine_num_columns(width)

    page = st.sidebar.selectbox("اختر القسم", [
        "إدارة المرضى 👥",
        "إدارة الأطباء 👨‍⚕️",
        "إدارة خطط العلاج 💊",
        "إدارة المواعيد 📅",
        "إدارة المخزون و الخامات 📦",
        "حسابات المرضى 🧾",
        "المحاسبة والمالية 💰",
        "التقارير 📊"
    ])

    if page == "إدارة المرضى 👥":
        patients_page(num_cols)
    elif page == "إدارة الأطباء 👨‍⚕️":
        doctors_page(num_cols)
    # تابع المنطق ونفذ باقي الصفحات بنفس النمط...

if __name__ == "__main__":
    main()
