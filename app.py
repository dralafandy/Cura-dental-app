# app.py
import streamlit as st
from utils import get_screen_width, determine_num_columns
from models import init_db

# Initialize database tables
init_db()

# Import page UIs, which you'll create as separate files later
import pages.patients_page as patients_page
import pages.doctors_page as doctors_page
import pages.treatments_page as treatments_page
import pages.appointments_page as appointments_page
import pages.accounting_page as accounting_page
import pages.reports_page as reports_page

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

screen_width = get_screen_width()
num_cols = determine_num_columns(screen_width)

st.sidebar.title("مرحباً بك في نظام إدارة العيادة الأسنانية 🦷")
page = st.sidebar.selectbox("اختر القسم", [
    "إدارة المرضى 👥",
    "إدارة الأطباء 👨‍⚕️",
    "إدارة خطط العلاج 💊",
    "إدارة المواعيد 📅",
    "المحاسبة 💰",
    "التقارير 📊"
])

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
