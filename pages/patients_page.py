import streamlit as st
import pandas as pd
from database import add_patient, edit_patient, delete_patient, get_patients

def show(num_cols):
    st.title("إدارة المرضى 👥")

    with st.expander("إضافة مريض جديد ➕", expanded=True):
        with st.form("إضافة مريض"):
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
        'id': p.id,
        'name': p.name,
        'age': p.age,
        'gender': p.gender,
        'phone': p.phone,
        'address': p.address
    } for p in patients])

    search_term = st.text_input("بحث عن مريض 🔍")
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف مريض ✏️🗑️"):
        patient_id = st.number_input("معرف المريض للتعديل/الحذف", min_value=1)
        patient = next((p for p in patients if p.id == patient_id), None)

        if patient:
            with st.form("تعديل مريض"):
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
