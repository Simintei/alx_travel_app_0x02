import requests
from django.http import JsonResponse
from django.views import View
from django.conf import settings
import uuid
from rest_framework import viewsets
from .models import Listing, Booking, Payment
from .serializers import ListingSerializer, BookingSerializer

class ListingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Listings
    Provides CRUD operations
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Bookings
    Provides CRUD operations
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer


class InitiatePaymentView(View):
    """
    API endpoint that initiates a payment using Chapa.
    """

    def post(self, request, *args, **kwargs):
        # Retrieve POST data
        data = request.POST
        booking_reference = data.get("booking_reference")
        amount = data.get("amount")
        email = data.get("email")
        name = data.get("name")

        # Validate required fields
        if not all([booking_reference, amount, email, name]):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Generate unique transaction reference
        tx_ref = f"TX-{uuid.uuid4().hex[:10]}"

        # Create Payment record (status = Pending)
        payment = Payment.objects.create(
            booking_reference=booking_reference,
            amount=amount,
            transaction_id=tx_ref,
            status="Pending",
        )

        # Prepare Chapa request payload
        payload = {
            "amount": amount,
            "currency": "ETB",  # Change if using another currency
            "email": email,
            "first_name": name,
            "tx_ref": tx_ref,
            "callback_url": "http://127.0.0.1:8000/api/verify-payment/",
            "customization": {
                "title": "Travel Booking Payment",
                "description": f"Payment for booking {booking_reference}",
            },
        }

        headers = {
            "Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}",
            "Content-Type": "application/json",
        }

        # Send request to Chapa
        response = requests.post(
            "https://api.chapa.co/v1/transaction/initialize",
            json=payload,
            headers=headers,
        )

        resp_json = response.json()

        # Handle success
        if resp_json.get("status") == "success":
            checkout_url = resp_json["data"]["checkout_url"]
            return JsonResponse({
                "message": "Payment initiated successfully.",
                "transaction_id": tx_ref,
                "checkout_url": checkout_url
            })

        # Handle failure
        payment.status = "Failed"
        payment.save()
        return JsonResponse({
            "error": "Failed to initiate payment.",
            "details": resp_json
        }, status=400)


class VerifyPaymentView(View):
    """
    Verifies payment status with Chapa after user completes payment.
    """

    def get(self, request, *args, **kwargs):
        tx_ref = request.GET.get("tx_ref")

        if not tx_ref:
            return JsonResponse({"error": "Transaction reference (tx_ref) is required"}, status=400)

        try:
            payment = Payment.objects.get(transaction_id=tx_ref)
        except Payment.DoesNotExist:
            return JsonResponse({"error": "Payment not found"}, status=404)

        # Call Chapa API to verify payment
        headers = {"Authorization": f"Bearer {settings.CHAPA_SECRET_KEY}"}
        url = f"https://api.chapa.co/v1/transaction/verify/{tx_ref}"

        response = requests.get(url, headers=headers)
        resp_json = response.json()

        if resp_json.get("status") == "success":
            chapa_status = resp_json["data"]["status"]

            if chapa_status == "success":
                payment.status = "Completed"
                payment.save()

                # Optionally send confirmation email asynchronously
                from .tasks import send_payment_confirmation_email
                send_payment_confirmation_email.delay(payment.id)

                return JsonResponse({
                    "message": "Payment verified successfully.",
                    "status": "Completed",
                    "transaction_id": tx_ref
                })
            else:
                payment.status = "Failed"
                payment.save()
                return JsonResponse({"message": "Payment verification failed."}, status=400)

        return JsonResponse({
            "error": "Unable to verify payment.",
            "details": resp_json
        }, status=400)


