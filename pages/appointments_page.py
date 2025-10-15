import streamlit as st
import pandas as pd
import datetime
from database import get_patients, get_doctors, get_treatments, add_appointment, get_appointments, edit_appointment, delete_appointment

def show(num_cols):
    st.title("إدارة المواعيد 📅")

    with st.expander("إضافة موعد جديد ➕", expanded=True):
        with st.form("إضافة موعد"):
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
            with st.form("تعديل موعد"):
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
