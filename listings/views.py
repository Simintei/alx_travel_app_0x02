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

class PaymentViewSet(viewsets.ModelViewSet):
    """
    API endpoint for Payment
    Provides CRUD operations
    """
    queryset = Payment.objects.all()
    serialzer_class = PaymentSerualizer
    

