import streamlit as st
import pandas as pd
from database import get_appointments
from payments import add_payment, get_payments

def show(num_cols):
    st.title("المحاسبة 💰")

    appointments = get_appointments()

    with st.expander("إنشاء فاتورة جديدة ➕", expanded=True):
        with st.form("إنشاء فاتورة"):
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
