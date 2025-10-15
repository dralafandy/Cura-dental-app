# payments.py
from database import calculate_shares, Session
from models import Payment
import datetime

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
