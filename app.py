# app.py
import streamlit as st
from utils import get_screen_width, determine_num_columns

# استدعاء صفحات التطبيق (تأكد من وجود __init__.py في مجلد pages)
import pages.patients_page as patients_page
import pages.doctors_page as doctors_page
import pages.treatments_page as treatments_page
import pages.appointments_page as appointments_page
import pages.accounting_page as accounting_page
import pages.reports_page as reports_page

# إعداد الصفحة
st.set_page_config(layout="wide", page_title="إدارة عيادة الأسنان 🦷", page_icon="🦷")

# التنسيق العام
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
/* استجابة للشاشات الصغيرة */
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

# الحصول على عرض الشاشة وعدد الأعمدة المناسب للتخطيط
screen_width = get_screen_width()
num_cols = determine_num_columns(screen_width)

# الشريط الجانبي لاختيار القسم
st.sidebar.title("مرحباً بك في نظام إدارة العيادة الأسنانية 🦷")
page = st.sidebar.selectbox("اختر القسم", [
    "إدارة المرضى 👥",
    "إدارة الأطباء 👨‍⚕️",
    "إدارة خطط العلاج 💊",
    "إدارة المواعيد 📅",
    "المحاسبة 💰",
    "التقارير 📊"
])

# توجيه لكل صفحة اعتماداً على اختيار المستخدم
if page == "إدارة المرضى 👥":
    patients_page.show(num_cols)
elif page == "إدارة الأطباء 👨‍⚕️":
    doctors_page.show(num_cols)
elif page == "إدارة خطط العلاج 💊":
    treatments_page.show(num_cols)
elif page == "إدارة المواعيد 📅":
    appointments_page.show(num_cols)
elif page == "المحاسبة 💰":
    accounting_page.show(num_cols)
elif page == "التقارير 📊":
    reports_page.show(num_cols)
