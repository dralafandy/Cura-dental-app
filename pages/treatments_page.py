import streamlit as st
import pandas as pd
from database import add_treatment, edit_treatment, delete_treatment, get_treatments, add_treatment_percentage, get_doctors

def show(num_cols):
    st.title("إدارة خطط العلاج 💊")

    with st.expander("إضافة علاج جديد ➕", expanded=True):
        with st.form("إضافة علاج"):
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
        'id': t.id,
        'name': t.name,
        'base_cost': t.base_cost
    } for t in treatments])

    search_term = st.text_input("بحث عن علاج 🔍")
    if search_term:
        df = df[df.apply(lambda row: search_term.lower() in ' '.join(row.astype(str)).lower(), axis=1)]

    st.dataframe(df, use_container_width=True)

    with st.expander("تعديل أو حذف علاج ✏️🗑️"):
        treatment_id = st.number_input("معرف العلاج", min_value=1)
        treatment = next((t for t in treatments if t.id == treatment_id), None)

        if treatment:
            with st.form("تعديل علاج"):
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
    with st.form("إضافة نسب"):
        treatment_opt = st.selectbox("العلاج", options=[(t.name, t.id) for t in treatments], format_func=lambda x: x[0])
        doctor_opt = st.selectbox("الطبيب", options=[(d.name, d.id) for d in doctors], format_func=lambda x: x[0])
        clinic_perc = st.number_input("نسبة العيادة (%)", 0.0, 100.0, value=50.0)
        doctor_perc = st.number_input("نسبة الطبيب (%)", 0.0, 100.0, value=50.0)
        if st.form_submit_button("إضافة"):
            if clinic_perc + doctor_perc != 100:
                st.error("يجب أن يكون مجموع النسب 100%")
            else:
                add_treatment_percentage(treatment_opt[1], doctor_opt[1], clinic_perc, doctor_perc)
                st.success("تم إضافة النسب ✅")
