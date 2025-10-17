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

    

