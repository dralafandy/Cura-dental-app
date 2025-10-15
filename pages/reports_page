import streamlit as st
import pandas as pd
import plotly.express as px
from reports import generate_report, export_to_excel, export_to_pdf

def show(num_cols):
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
