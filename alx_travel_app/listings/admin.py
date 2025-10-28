from django.contrib import admin
from .models import Listing, Booking, Review, Payment


@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ('title', 'host', 'location', 'price_per_night', 'is_available', 'created_at')
    list_filter = ('is_available', 'location', 'created_at')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('listing_id', 'created_at', 'updated_at')


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'listing', 'guest', 'check_in_date', 'check_out_date', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at', 'check_in_date')
    search_fields = ('guest__username', 'listing__title', 'booking_id')
    readonly_fields = ('booking_id', 'created_at')
    date_hierarchy = 'check_in_date'


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('listing', 'reviewer', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('listing__title', 'reviewer__username', 'comment')
    readonly_fields = ('review_id', 'created_at')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'booking', 'amount', 'currency', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'currency', 'created_at')
    search_fields = ('payment_id', 'booking__booking_id', 'transaction_id', 'chapa_reference')
    readonly_fields = ('payment_id', 'transaction_id', 'created_at', 'updated_at', 'completed_at')
    date_hierarchy = 'created_at'
    fieldsets = (
        ('Payment Information', {
            'fields': ('payment_id', 'booking', 'amount', 'currency')
        }),
        ('Status', {
            'fields': ('status', 'error_message')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'chapa_reference', 'payment_method')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )

