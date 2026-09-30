from django.urls import path
from . import views

urlpatterns = [

    path(
        "search/",
        views.search_hotels
    ),

    path(
        "search-anywhere/",
        views.search_anywhere
    ),

    path(
        "add/",
        views.add_hotel
    ),

    path(
        "update/<int:hotel_id>/",
        views.update_hotel
    ),

    path(
        "delete/<int:hotel_id>/",
        views.delete_hotel
    ),

    path(
        "hotel/<int:hotel_id>/",
        views.hotel_detail
    ),

    path(
        "book/",
        views.create_booking
    ),

    path(
        "bookings/",
        views.get_bookings
    ),
]