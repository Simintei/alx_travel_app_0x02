from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet, InitiatePaymentView, VerifyPaymentView

# Create a router and register our viewsets with it
router = DefaultRouter()
router.register(r'listings', ListingViewSet, basename='listing')
router.register(r'bookings', BookingViewSet, basename='booking')

# The API URLs are determined automatically by the router
urlpatterns = [
    path('', include(router.urls)),
    path('initiate-payment/', InitiatePaymentView.as_view(), name='initiate-payment'),
    path('verify-payment/', VerifyPaymentView.as_view(), name='verify-payment'),

]
