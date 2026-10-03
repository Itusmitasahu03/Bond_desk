from django.urls import path
from . import views


urlpatterns = [

    # =========================
    # HOTEL ROUTES
    # =========================

    path("search/", views.search_hotels, name="search_hotels"),

    path(
        "search-anywhere/",
        views.search_anywhere,
        name="search_anywhere"
    ),

    path(
        "add/",
        views.add_hotel,
        name="add_hotel"
    ),

    path(
        "update/<int:hotel_id>/",
        views.update_hotel,
        name="update_hotel"
    ),

    path(
        "delete/<int:hotel_id>/",
        views.delete_hotel,
        name="delete_hotel"
    ),

    path(
        "hotel/<int:hotel_id>/",
        views.hotel_detail,
        name="hotel_detail"
    ),


    # =========================
    # BOOKING ROUTES
    # =========================

    path(
        "book/",
        views.create_booking,
        name="create_booking"
    ),

    path(
        "bookings/",
        views.get_bookings,
        name="get_bookings"
    ),


    # =========================
    # JOB ROUTES
    # =========================

    path(
        "jobs/",
        views.search_jobs,
        name="search_jobs"
    ),

    path(
        "jobs/<int:job_id>/",
        views.job_detail,
        name="job_detail"
    ),

    path(
        "jobs/add/",
        views.add_job,
        name="add_job"
    ),
    path(
    "debug-urls/",
    views.debug_urls,
    name="debug_urls"
),
]