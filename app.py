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

# --- Database Setup ---

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

Base.metadata.create_all(engine)


# --- Utility Functions ---

def get_screen_width():
    width = st_js.st_javascript("window.innerWidth")
    if width is None:
        return 800
    return width

def determine_num_columns(width):
    if width < 600:
        return 1
    elif width < 1000:
        return 2
    else:
        return 3


# --- DB CRUD Functions ---

# Patients
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


# Doctors
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


# Treatments
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


# Treatment Percentages
def add_treatment_percentage(treatment_id, doctor_id, clinic_percentage, doctor_percentage):
    session = Session()
    perc = TreatmentPercentage(treatment_id=treatment_id, doctor_id=doctor_id,
                               clinic_percentage=clinic_percentage, doctor_percentage=doctor_percentage)
    session.add(perc)
    session.commit()
    session.close()


# Appointments
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


# Payments
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


# --- Reports and Exports ---

def generate_report(start_date, end_date):
    session = Session()
    payments = session.query(Payment).filter(
        Payment.date_paid.between(start_date, end_date)).all()
    data = []
    for p in payments:
        data.append({
            'موعد': p.appointment_id,
            'إجمالي': p.total_amount,
            'نصيب العيادة': p.clinic_share,
            'نصيب الطبيب': p.doctor_share,
            'تاريخ': p.date_paid
        })
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


# --- Streamlit UI ---

st.set_page_config(layout="wide", page_title="إدارة عيادة الأسنان 🦷", page_icon="🦷")

st.markdown("""
<style>
html, body, [class*="css"]  {
    text-align: right;
    direction: rtl;
    font-family: 'Arial', sans-serif;
}
.stButton > button {
    width: 100%;
    border-radius: 8px;
}
.stDataFrame {
    width: 100%;
}
/* media queries for mobile */
@media (max-width: 768px) {
    .st-expander {
        width: 100%;
    }
    .st-columns > div {
        flex-direction: column;
    }
}
</style>
""", unsafe_allow_html=True)


ui_width = get_screen_width()
num_cols = determine_num_columns(ui_width)

st.sidebar.title("مرحباً بك في نظام إدارة العيادة الأسنانية 🦷")

page = st.sidebar.selectbox("اختر القسم", [
    "إدارة المرضى 👥",
    "إدارة الأطباء 👨‍⚕️",
    "إدارة خطط العلاج 💊",
    "إدارة المواعيد 📅",
    "المحاسبة 💰",
    "التقارير 📊"
])

# === Patients Page ===
def patients_page():
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
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف مريض ✏️🗑️"):
        patient_id = st.number_input("معرف المريض للتعديل/الحذف", min_value=1)
        patient = next((p for p in patients if p.id == patient_id), None)

        if patient:
            with st.form("edit_patient"):
                name = st.text_input("الاسم", value=patient.name)
                age = st.number_input("العمر", value=patient.age, min_value=0)
                gender = st.selectbox("الجنس", ["ذكر", "أنثى"], index=0 if patient.gender == "ذكر" else 1)
                phone = st.text_input("الهاتف", value=patient.phone)
                address = st.text_input("العنوان", value=patient.address)
                medical_history = st.text_area("التاريخ الطبي", value=patient.medical_history)
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
            st.info("الرجاء إدخال معرف مريض صحيح للتعديل أو الحذف")


# === Doctors Page ===
def doctors_page():
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
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف طبيب ✏️🗑️"):
        doctor_id = st.number_input("معرف الطبيب", min_value=1)
        doctor = next((d for d in doctors if d.id == doctor_id), None)

        if doctor:
            with st.form("edit_doctor"):
                name = st.text_input("الاسم", value=doctor.name)
                specialty = st.text_input("التخصص", value=doctor.specialty)
                phone = st.text_input("الهاتف", value=doctor.phone)
                email = st.text_input("البريد الإلكتروني", value=doctor.email)

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
            st.info("الرجاء إدخال معرف طبيب صحيح للتعديل أو الحذف")


# === Treatments Page ===
def treatments_page():
    st.title("إدارة خطط العلاج 💊")

    with st.expander("إضافة علاج جديد ➕", expanded=True):
        with st.form("add_treatment"):
            name = st.text_input("اسم العلاج")
            base_cost = st.number_input("التكلفة الأساسية", min_value=0.0)

            if st.form_submit_button("إضافة"):
                if not name:
                    st.error("الرجاء إدخال اسم العلاج")
                else:
                    add_treatment(name, base_cost)
                    st.success("تم إضافة العلاج ✅")

    treatments = get_treatments()
    df = pd.DataFrame([{
        'id': t.id, 'name': t.name, 'base_cost': t.base_cost
    } for t in treatments])

    search_term = st.text_input("بحث عن علاج 🔍")
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف علاج ✏️🗑️"):
        treatment_id = st.number_input("معرف العلاج", min_value=1)
        treatment = next((t for t in treatments if t.id == treatment_id), None)

        if treatment:
            with st.form("edit_treatment"):
                name = st.text_input("اسم العلاج", value=treatment.name)
                base_cost = st.number_input("التكلفة الأساسية", value=treatment.base_cost)

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("تعديل"):
                        edit_treatment(treatment_id, name, base_cost)
                        st.success("تم التعديل ✅")
                with col2:
                    if st.form_submit_button("حذف"):
                        delete_treatment(treatment_id)
                        st.success("تم الحذف ✅")
        else:
            st.info("الرجاء إدخال معرف علاج صحيح للتعديل أو الحذف")

    st.subheader("تخصيص النسب المئوية 📊")
    doctors = get_doctors()
    with st.form("add_percentages"):
        treatment_opt = st.selectbox("العلاج",
            options=[(t.name, t.id) for t in treatments], format_func=lambda x: x[0])
        doctor_opt = st.selectbox("الطبيب",
            options=[(d.name, d.id) for d in doctors], format_func=lambda x: x[0])
        clinic_perc = st.number_input("نسبة العيادة (%)", 0.0, 100.0, value=50.0)
        doctor_perc = st.number_input("نسبة الطبيب (%)", 0.0, 100.0, value=50.0)
        if st.form_submit_button("إضافة"):
            if clinic_perc + doctor_perc != 100:
                st.error("يجب أن يكون مجموع النسب 100%")
            else:
                add_treatment_percentage(treatment_opt[1], doctor_opt[1], clinic_perc, doctor_perc)
                st.success("تم إضافة النسب ✅")


# === Appointments Page ===
def appointments_page():
    st.title("إدارة المواعيد 📅")

    with st.expander("إضافة موعد جديد ➕", expanded=True):
        with st.form("add_appointment"):
            patients = get_patients()
            doctors = get_doctors()
            treatments = get_treatments()

            cols = st.columns(num_cols)
            with cols[0]:
                patient_opt = st.selectbox("المريض", options=[(p.name, p.id) for p in patients], format_func=lambda x: x[0])
                doctor_opt = st.selectbox("الطبيب", options=[(d.name, d.id) for d in doctors], format_func=lambda x: x[0])
            if num_cols > 1:
                with cols[1]:
                    treatment_opt = st.selectbox("العلاج", options=[(t.name, t.id) for t in treatments], format_func=lambda x: x[0])
                    date = st.date_input("التاريخ")
            if num_cols > 2:
                with cols[2]:
                    time = st.time_input("الوقت")

            status = st.selectbox("الحالة", ["مؤكد", "ملغى", "قيد الانتظار"])
            notes = st.text_area("ملاحظات")

            if st.form_submit_button("إضافة"):
                full_date = datetime.datetime.combine(date, time)
                add_appointment(patient_opt[1], doctor_opt[1], treatment_opt[1], full_date, status, notes)
                st.success("تم إضافة الموعد ✅")

    appointments = get_appointments()
    df = pd.DataFrame([{
        'id': a.id,
        'patient': a.patient.name if a.patient else '',
        'doctor': a.doctor.name if a.doctor else '',
        'treatment': a.treatment.name if a.treatment else '',
        'date': a.date,
        'status': a.status
    } for a in appointments])

    search_term = st.text_input("بحث عن موعد 🔍")
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف موعد ✏️🗑️"):
        appointment_id = st.number_input("معرف الموعد", min_value=1)
        appointment = next((a for a in appointments if a.id == appointment_id), None)

        if appointment:
            with st.form("edit_appointment"):
                patients = get_patients()
                doctors = get_doctors()
                treatments = get_treatments()

                patient_opt = st.selectbox("المريض", options=[(p.name, p.id) for p in patients], format_func=lambda x: x[0], index=[p.id for p in patients].index(appointment.patient_id))
                doctor_opt = st.selectbox("الطبيب", options=[(d.name, d.id) for d in doctors], format_func=lambda x: x[0], index=[d.id for d in doctors].index(appointment.doctor_id))
                treatment_opt = st.selectbox("العلاج", options=[(t.name, t.id) for t in treatments], format_func=lambda x: x[0], index=[t.id for t in treatments].index(appointment.treatment_id))
                date = st.date_input("التاريخ", value=appointment.date.date())
                time = st.time_input("الوقت", value=appointment.date.time())
                status = st.selectbox("الحالة", ["مؤكد", "ملغى", "قيد الانتظار"], index=["مؤكد", "ملغى", "قيد الانتظار"].index(appointment.status))
                notes = st.text_area("ملاحظات", value=appointment.notes)

                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("تعديل"):
                        full_date = datetime.datetime.combine(date, time)
                        edit_appointment(appointment_id, patient_opt[1], doctor_opt[1], treatment_opt[1], full_date, status, notes)
                        st.success("تم التعديل ✅")
                with col2:
                    if st.form_submit_button("حذف"):
                        delete_appointment(appointment_id)
                        st.success("تم الحذف ✅")
        else:
            st.info("الرجاء إدخال معرف موعد صحيح للتعديل أو الحذف")


# === Accounting Page ===
def accounting_page():
    st.title("المحاسبة 💰")

    appointments = get_appointments()

    with st.expander("إنشاء فاتورة جديدة ➕", expanded=True):
        with st.form("create_invoice"):
            appointment_opt = st.selectbox("اختر الموعد", options=[(f"{a.id} - {a.patient.name if a.patient else 'غير معروف'} ({a.date})", a.id) for a in appointments])
            total_amount = st.number_input("المبلغ الإجمالي", min_value=0.0)
            paid_amount = st.number_input("المبلغ المدفوع", min_value=0.0)
            discounts = st.number_input("الخصومات", min_value=0.0)
            taxes = st.number_input("الضرائب", min_value=0.0)
            payment_method = st.selectbox("طريقة الدفع", ["نقدي", "بطاقة", "تحويل"])

            if st.form_submit_button("إنشاء"):
                add_payment(appointment_opt[1], total_amount, paid_amount, payment_method, discounts, taxes)
                st.success("تم إنشاء الفاتورة مع حساب النسب ✅")

    payments = get_payments()
    df = pd.DataFrame([{
        'id': p.id,
        'موعد': p.appointment_id,
        'إجمالي': p.total_amount,
        'مدفوع': p.paid_amount,
        'نصيب العيادة': p.clinic_share,
        'نصيب الطبيب': p.doctor_share
    } for p in payments])
    st.dataframe(df, use_container_width=True)


# === Reports Page ===
def reports_page():
    st.title("التقارير 📊")

    start_date = st.date_input("من تاريخ")
    end_date = st.date_input("إلى تاريخ")

    if st.button("إنشاء تقرير"):
        df = generate_report(start_date, end_date)
        st.dataframe(df, use_container_width=True)

        if not df.empty:
            fig = px.line(df, x='تاريخ', y=['إجمالي', 'نصيب العيادة', 'نصيب الطبيب'], title="الإيرادات مع مرور الوقت 📈")
            st.plotly_chart(fig, use_container_width=True)

        excel_buffer = export_to_excel(df)
        st.download_button("تصدير إلى Excel 📥", data=excel_buffer, file_name="report.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        pdf_buffer = export_to_pdf(df)
        st.download_button("تصدير إلى PDF 📥", data=pdf_buffer, file_name="report.pdf", mime="application/pdf")

# --- Main app switch ---
if page == "إدارة المرضى 👥":
    patients_page()
elif page == "إدارة الأطباء 👨‍⚕️":
    doctors_page()
elif page == "إدارة خطط العلاج 💊":
    treatments_page()
elif page == "إدارة المواعيد 📅":
    appointments_page()
elif page == "المحاسبة 💰":
    accounting_page()
elif page == "التقارير 📊":
    reports_page()
