from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django.db.models import Q
from .models import Listing, Booking, Review
from .serializers import ListingSerializer, BookingSerializer, ReviewSerializer


class ListingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel property listings.
    
    Provides CRUD operations:
    - GET /api/listings/ - List all listings
    - POST /api/listings/ - Create a new listing
    - GET /api/listings/{id}/ - Retrieve a specific listing
    - PUT /api/listings/{id}/ - Update a listing
    - DELETE /api/listings/{id}/ - Delete a listing
    
    Additional actions:
    - GET /api/listings/{id}/reviews/ - Get reviews for a listing
    """
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['location', 'is_available']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'price_per_night', 'title']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Automatically set the host to the current user when creating a listing"""
        serializer.save(host=self.request.user)

    def perform_update(self, serializer):
        """Allow only the listing host to update their listing"""
        if serializer.instance.host != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own listings.")
        serializer.save()

    def perform_destroy(self, instance):
        """Allow only the listing host to delete their listing"""
        if instance.host != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own listings.")
        instance.delete()

    @action(detail=True, methods=['get'])
    def reviews(self, request, pk=None):
        """Get all reviews for a specific listing"""
        listing = self.get_object()
        reviews = listing.reviews.all()
        serializer = ReviewSerializer(reviews, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        """Get all listings created by the current user"""
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Authentication required.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        listings = Listing.objects.filter(host=request.user)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def available(self, request):
        """Get all available listings"""
        listings = Listing.objects.filter(is_available=True)
        serializer = self.get_serializer(listings, many=True)
        return Response(serializer.data)


class BookingViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing travel bookings.
    
    Provides CRUD operations:
    - GET /api/bookings/ - List all bookings
    - POST /api/bookings/ - Create a new booking
    - GET /api/bookings/{id}/ - Retrieve a specific booking
    - PUT /api/bookings/{id}/ - Update a booking
    - DELETE /api/bookings/{id}/ - Delete a booking
    
    Additional actions:
    - GET /api/bookings/my_bookings/ - Get bookings made by the current user
    - PATCH /api/bookings/{id}/cancel/ - Cancel a booking
    """
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'listing', 'guest']
    ordering_fields = ['created_at', 'check_in_date', 'total_price']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Automatically set the guest to the current user when creating a booking"""
        # Get listing from write_only field
        listing_id = self.request.data.get('listing_id')
        from .models import Listing
        listing = Listing.objects.get(listing_id=listing_id)
        
        # Calculate total_price if not provided
        total_price = serializer.validated_data.get('total_price')
        if not total_price and listing:
            from datetime import datetime
            check_in = serializer.validated_data['check_in_date']
            check_out = serializer.validated_data['check_out_date']
            days = (check_out - check_in).days
            total_price = listing.price_per_night * days
        
        serializer.save(guest=self.request.user, listing=listing, total_price=total_price)

    def get_queryset(self):
        """Filter bookings based on user role"""
        user = self.request.user
        if user.is_authenticated:
            # Users can see their own bookings and bookings for their listings
            return Booking.objects.filter(
                Q(guest=user) | Q(listing__host=user)
            ).distinct()
        return Booking.objects.none()

    @action(detail=False, methods=['get'])
    def my_bookings(self, request):
        """Get all bookings made by the current user"""
        bookings = Booking.objects.filter(guest=request.user)
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def cancel(self, request, pk=None):
        """Cancel a booking (change status to 'cancelled')"""
        booking = self.get_object()
        
        # Only guest or listing host can cancel
        if booking.guest != request.user and booking.listing.host != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only cancel your own bookings or bookings for your listings.")
        
        # Only pending or confirmed bookings can be cancelled
        if booking.status not in ['pending', 'confirmed']:
            return Response(
                {'detail': f'Cannot cancel a {booking.status} booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'cancelled'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'])
    def confirm(self, request, pk=None):
        """Confirm a pending booking (host only)"""
        booking = self.get_object()
        
        # Only listing host can confirm
        if booking.listing.host != request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Only the listing host can confirm bookings.")
        
        # Only pending bookings can be confirmed
        if booking.status != 'pending':
            return Response(
                {'detail': f'Cannot confirm a {booking.status} booking.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        booking.status = 'confirmed'
        booking.save()
        serializer = self.get_serializer(booking)
        return Response(serializer.data)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing listing reviews.
    
    Provides CRUD operations:
    - GET /api/reviews/ - List all reviews
    - POST /api/reviews/ - Create a new review
    - GET /api/reviews/{id}/ - Retrieve a specific review
    - PUT /api/reviews/{id}/ - Update a review
    - DELETE /api/reviews/{id}/ - Delete a review
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filterset_fields = ['listing', 'reviewer', 'rating']
    ordering_fields = ['created_at', 'rating']
    ordering = ['-created_at']

    def perform_create(self, serializer):
        """Automatically set the reviewer to the current user"""
        serializer.save(reviewer=self.request.user)

    def perform_update(self, serializer):
        """Allow only the reviewer to update their review"""
        if serializer.instance.reviewer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only update your own reviews.")
        serializer.save()

    def perform_destroy(self, instance):
        """Allow only the reviewer to delete their review"""
        if instance.reviewer != self.request.user:
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("You can only delete your own reviews.")
        instance.delete()
