from django.contrib import admin
from .models import Hotel, Booking


@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        'name',
        'location',
        'price',
        'rating',
        'available_rooms'
    )

    search_fields = (
        'name',
        'location'
    )

    list_filter = (
        'location',
        'rating'
    )


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        'customer_name',
        'hotel',
        'customer_phone',
        'check_in',
        'check_out',
        'rooms',
        'guests',
        'total_amount',
        'created_at'
    )

    search_fields = (
        'customer_name',
        'customer_email',
        'customer_phone'
    )

    list_filter = (
        'check_in',
        'check_out'
    )