from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Listing, Booking, Review


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ReviewSerializer(serializers.ModelSerializer):
    reviewer = UserSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True, required=False)
    listing = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Review
        fields = ['review_id', 'listing', 'listing_id', 'reviewer', 'rating', 'comment', 'created_at']

    def get_listing(self, obj):
        """Return basic listing info in read response"""
        return {
            'listing_id': obj.listing.listing_id,
            'title': obj.listing.title
        }

    def create(self, validated_data):
        """Create review with listing from write_only field"""
        listing_id = validated_data.pop('listing_id', None)
        if listing_id:
            from .models import Listing
            listing = Listing.objects.get(listing_id=listing_id)
            validated_data['listing'] = listing
        return super().create(validated_data)


class ListingSerializer(serializers.ModelSerializer):
    host = UserSerializer(read_only=True)
    reviews = ReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = [
            'listing_id', 'title', 'description', 'price_per_night', 'location',
            'amenities', 'host', 'created_at', 'updated_at', 'is_available',
            'reviews', 'average_rating', 'review_count'
        ]

    def get_average_rating(self, obj):
        reviews = obj.reviews.all()
        if reviews:
            return sum(review.rating for review in reviews) / len(reviews)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.count()


class BookingSerializer(serializers.ModelSerializer):
    listing = ListingSerializer(read_only=True)
    guest = UserSerializer(read_only=True)
    listing_id = serializers.UUIDField(write_only=True)

    class Meta:
        model = Booking
        fields = [
            'booking_id', 'listing', 'listing_id', 'guest', 'check_in_date',
            'check_out_date', 'total_price', 'status', 'created_at'
        ]

    def validate(self, data):
        if data['check_in_date'] >= data['check_out_date']:
            raise serializers.ValidationError("Check-out date must be after check-in date.")
        return data
