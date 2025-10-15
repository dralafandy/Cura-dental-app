import streamlit as st
import pandas as pd
from database import add_doctor, edit_doctor, delete_doctor, get_doctors

def show(num_cols):
    st.title("إدارة الأطباء 👨‍⚕️")

    with st.expander("إضافة طبيب جديد ➕", expanded=True):
        with st.form("إضافة طبيب"):
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
        'id': d.id,
        'name': d.name,
        'specialty': d.specialty,
        'phone': d.phone,
        'email': d.email
    } for d in doctors])

    search_term = st.text_input("بحث عن طبيب 🔍")
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف طبيب ✏️🗑️"):
        doctor_id = st.number_input("معرف الطبيب", min_value=1)
        doctor = next((d for d in doctors if d.id == doctor_id), None)

        if doctor:
            with st.form("تعديل طبيب"):
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
