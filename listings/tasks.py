from celery import shared_task
from django.core.mail import send_mail
from .models import Payment


@shared_task
def send_payment_confirmation_email(payment_id):
    try:
        payment = Payment.objects.get(id=payment_id)
        subject = "Payment Confirmation"
        message = f"""
        Dear Customer,

        Your payment for booking reference {payment.booking_reference} was successful.
        Amount: {payment.amount}
        Transaction ID: {payment.transaction_id}
        Status: {payment.status}

        Thank you for your booking!
        """
        recipient = ["user@example.com"]  # Replace with actual user email if available
        send_mail(subject, message, "no-reply@travelapp.com", recipient)
        return f"Payment confirmation email sent for {payment.transaction_id}"
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} not found."
