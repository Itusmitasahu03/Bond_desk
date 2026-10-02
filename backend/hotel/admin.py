from django.contrib import admin
from .models import Hotel, Booking, Job


# ============================================================
# HOTEL ADMIN
# ============================================================

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "location",
        "price",
        "available_rooms",
        "rating",
    )

    search_fields = (
        "name",
        "location",
        "description",
        "amenities",
    )


# ============================================================
# BOOKING ADMIN
# ============================================================

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):

    list_display = (
        "customer_name",
        "customer_email",
        "customer_phone",
        "hotel",
        "check_in",
        "check_out",
        "rooms",
        "created_at",
    )

    search_fields = (
        "customer_name",
        "customer_email",
        "customer_phone",
        "hotel__name",
    )


# ============================================================
# JOB ADMIN
# ============================================================

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "company",
        "location",
        "job_type",
        "work_mode",
        "salary",
        "created_at",
    )

    search_fields = (
        "title",
        "company",
        "location",
        "job_type",
        "skills",
    )

    list_filter = (
        "job_type",
        "work_mode",
        "location",
    )

    ordering = (
        "-created_at",
    )