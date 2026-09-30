from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from django.db.models import Q

from .models import Hotel, Booking

import json
import requests
from datetime import date


# ============================================================
# CALCULATE AVAILABLE ROOMS
# ============================================================

def get_available_rooms(hotel, check_in, check_out):

    # No dates selected = show total rooms
    if not check_in or not check_out:
        return hotel.available_rooms

    try:
        check_in_date = date.fromisoformat(check_in)
        check_out_date = date.fromisoformat(check_out)

    except ValueError:
        return 0

    if check_out_date <= check_in_date:
        return 0

    overlapping_bookings = Booking.objects.filter(
        hotel=hotel,
        check_in__lt=check_out_date,
        check_out__gt=check_in_date
    )

    booked_rooms = sum(
        booking.rooms
        for booking in overlapping_bookings
    )

    return max(
        hotel.available_rooms - booked_rooms,
        0
    )


# ============================================================
# SEARCH BOND_DESK DATABASE
# ============================================================

def search_hotels(request):

    location = request.GET.get("location", "").strip()
    check_in = request.GET.get("check_in", "").strip()
    check_out = request.GET.get("check_out", "").strip()

    if location:

        words = [
            word
            for word in location.replace(",", " ").split()
            if len(word.strip()) >= 2
        ]

        hotels = Hotel.objects.all()

        for word in words:
            hotels = hotels.filter(
                Q(location__icontains=word)
                | Q(name__icontains=word)
                | Q(description__icontains=word)
                | Q(amenities__icontains=word)
            )

    else:
        hotels = Hotel.objects.all()

    data = []

    for hotel in hotels:

        available_rooms = get_available_rooms(
            hotel,
            check_in,
            check_out
        )

        data.append({
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "price": float(hotel.price),
            "image_url": hotel.image_url,
            "phone": hotel.phone,
            "description": hotel.description,
            "amenities": hotel.amenities,
            "available_rooms": available_rooms,
            "total_rooms": hotel.available_rooms,
            "rating": float(hotel.rating),
            "source": "bond_desk",
            "bookable": available_rooms > 0,
            "website": "",
            "map_url": ""
        })

    return JsonResponse(data, safe=False)


# ============================================================
# SEARCH ANYWHERE
# ============================================================

def search_anywhere(request):

    location = request.GET.get("location", "").strip()
    check_in = request.GET.get("check_in", "").strip()
    check_out = request.GET.get("check_out", "").strip()

    if not location:
        return JsonResponse(
            {"error": "Please enter a location."},
            status=400
        )

    # --------------------------------------------------------
    # 1. SEARCH BOND_DESK DATABASE
    # --------------------------------------------------------

    words = [
        word.strip()
        for word in location.replace(",", " ").split()
        if len(word.strip()) >= 2
    ]

    local_hotels = Hotel.objects.all()

    if words:

        for word in words:

            local_hotels = local_hotels.filter(
                Q(location__icontains=word)
                | Q(name__icontains=word)
                | Q(description__icontains=word)
                | Q(amenities__icontains=word)
            )

    results = []

    for hotel in local_hotels:

        available_rooms = get_available_rooms(
            hotel,
            check_in,
            check_out
        )

        results.append({
            "id": hotel.id,
            "name": hotel.name,
            "location": hotel.location,
            "price": float(hotel.price),
            "image_url": hotel.image_url,
            "phone": hotel.phone,
            "description": hotel.description,
            "amenities": hotel.amenities,
            "available_rooms": available_rooms,
            "total_rooms": hotel.available_rooms,
            "rating": float(hotel.rating),
            "source": "bond_desk",
            "bookable": available_rooms > 0,
            "website": "",
            "map_url": ""
        })

    # --------------------------------------------------------
    # 2. NOMINATIM LOCATION SEARCH
    # --------------------------------------------------------

    try:

        nominatim_url = (
            "https://nominatim.openstreetmap.org/search"
        )

        headers = {
            "User-Agent":
                "Bond_Desk/1.0 college-hotel-booking-project"
        }

        params = {
            "q": location,
            "format": "json",
            "limit": 1
        }

        response = requests.get(
            nominatim_url,
            params=params,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            return JsonResponse(
                results,
                safe=False
            )

        locations = response.json()

        if not locations:
            return JsonResponse(
                results,
                safe=False
            )

        latitude = float(
            locations[0]["lat"]
        )

        longitude = float(
            locations[0]["lon"]
        )

    except Exception as error:

        print(
            "Nominatim error:",
            error
        )

        return JsonResponse(
            results,
            safe=False
        )

    # --------------------------------------------------------
    # 3. OPENSTREETMAP OVERPASS
    # --------------------------------------------------------

    overpass_query = f"""
    [out:json][timeout:25];

    (
      nwr["tourism"="hotel"](around:15000,{latitude},{longitude});
      nwr["tourism"="hostel"](around:15000,{latitude},{longitude});
      nwr["tourism"="motel"](around:15000,{latitude},{longitude});
      nwr["tourism"="guest_house"](around:15000,{latitude},{longitude});
    );

    out center tags;
    """

    try:

        overpass_url = (
            "https://overpass-api.de/api/interpreter"
        )

        overpass_response = requests.post(
            overpass_url,
            data=overpass_query,
            headers=headers,
            timeout=40
        )

        if overpass_response.status_code != 200:
            return JsonResponse(
                results,
                safe=False
            )

        osm_data = overpass_response.json()

    except Exception as error:

        print(
            "Overpass error:",
            error
        )

        return JsonResponse(
            results,
            safe=False
        )

    # --------------------------------------------------------
    # 4. CONVERT OSM DATA
    # --------------------------------------------------------

    osm_hotels = []

    for place in osm_data.get(
        "elements",
        []
    ):

        tags = place.get(
            "tags",
            {}
        )

        name = tags.get(
            "name"
        )

        if not name:
            continue

        # Coordinates
        if (
            "lat" in place
            and
            "lon" in place
        ):

            place_lat = place["lat"]
            place_lon = place["lon"]

        elif "center" in place:

            place_lat = place["center"].get(
                "lat"
            )

            place_lon = place["center"].get(
                "lon"
            )

        else:

            place_lat = latitude
            place_lon = longitude

        # Address
        address_parts = []

        for key in [
            "addr:housenumber",
            "addr:street",
            "addr:suburb",
            "addr:city",
            "addr:state"
        ]:

            value = tags.get(key)

            if value:
                address_parts.append(value)

        address = ", ".join(
            address_parts
        )

        if not address:
            address = location

        # Phone
        phone = (
            tags.get("phone")
            or
            tags.get("contact:phone")
            or
            "Not available"
        )

        # Website
        website = (
            tags.get("website")
            or
            tags.get("contact:website")
            or
            ""
        )

        # Rating
        stars = tags.get(
            "stars"
        )

        try:

            rating = (
                float(stars)
                if stars
                else 0
            )

        except (
            TypeError,
            ValueError
        ):

            rating = 0

        # Rooms
        rooms = tags.get(
            "rooms"
        )

        try:

            rooms = (
                int(rooms)
                if rooms
                else 0
            )

        except (
            TypeError,
            ValueError
        ):

            rooms = 0

        # Hotel type
        hotel_type = (
            tags.get(
                "tourism",
                "hotel"
            )
            .replace(
                "_",
                " "
            )
            .title()
        )

        # OpenStreetMap URL
        map_url = (
            "https://www.openstreetmap.org/"
            f"?mlat={place_lat}"
            f"&mlon={place_lon}"
            f"#map=18/{place_lat}/{place_lon}"
        )

        osm_hotels.append({

            "id":
                f"osm_{place['type']}_{place['id']}",

            "name":
                name,

            "location":
                address,

            "price":
                None,

            "image_url":
                "https://images.unsplash.com/"
                "photo-1566073771259-6a8506099945"
                "?auto=format&fit=crop&w=1000&q=80",

            "phone":
                phone,

            "description":
                f"{hotel_type} found near {location}.",

            "amenities":
                "OpenStreetMap listing",

            "available_rooms":
                rooms,

            "total_rooms":
                rooms,

            "rating":
                rating,

            "source":
                "openstreetmap",

            "bookable":
                False,

            "website":
                website,

            "map_url":
                map_url
        })

    # --------------------------------------------------------
    # 5. REMOVE DUPLICATES
    # --------------------------------------------------------

    existing_names = {
        hotel["name"].strip().lower()
        for hotel in results
    }

    for hotel in osm_hotels:

        hotel_name = (
            hotel["name"]
            .strip()
            .lower()
        )

        if hotel_name not in existing_names:

            results.append(
                hotel
            )

            existing_names.add(
                hotel_name
            )

    return JsonResponse(
        results,
        safe=False
    )


# ============================================================
# ADD HOTEL
# ============================================================

@csrf_exempt
def add_hotel(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error":
                    "Only POST requests are allowed."
            },
            status=405
        )

    try:

        data = json.loads(
            request.body
        )

        hotel = Hotel.objects.create(

            name=data.get(
                "name",
                ""
            ).strip(),

            location=data.get(
                "location",
                ""
            ).strip(),

            price=data.get(
                "price",
                0
            ),

            image_url=data.get(
                "image_url",
                ""
            ).strip(),

            phone=data.get(
                "phone",
                ""
            ).strip(),

            description=data.get(
                "description",
                ""
            ).strip(),

            amenities=data.get(
                "amenities",
                ""
            ).strip(),

            available_rooms=data.get(
                "available_rooms",
                0
            ),

            rating=data.get(
                "rating",
                4.0
            )
        )

        return JsonResponse(
            {
                "message":
                    "Hotel added successfully.",

                "hotel_id":
                    hotel.id
            },
            status=201
        )

    except Exception as error:

        return JsonResponse(
            {
                "error":
                    str(error)
            },
            status=400
        )


# ============================================================
# UPDATE HOTEL
# ============================================================

@csrf_exempt
def update_hotel(request, hotel_id):

    if request.method != "PUT":

        return JsonResponse(
            {
                "error":
                    "Only PUT requests are allowed."
            },
            status=405
        )

    try:

        hotel = get_object_or_404(
            Hotel,
            id=hotel_id
        )

        data = json.loads(
            request.body
        )

        # Update fields only when supplied
        hotel.name = data.get(
            "name",
            hotel.name
        ).strip()

        hotel.location = data.get(
            "location",
            hotel.location
        ).strip()

        hotel.price = data.get(
            "price",
            hotel.price
        )

        hotel.phone = data.get(
            "phone",
            hotel.phone
        ).strip()

        hotel.available_rooms = data.get(
            "available_rooms",
            hotel.available_rooms
        )

        hotel.rating = data.get(
            "rating",
            hotel.rating
        )

        hotel.image_url = data.get(
            "image_url",
            hotel.image_url
        ).strip()

        hotel.amenities = data.get(
            "amenities",
            hotel.amenities
        ).strip()

        hotel.description = data.get(
            "description",
            hotel.description
        ).strip()

        hotel.save()

        return JsonResponse({

            "message":
                "Hotel updated successfully.",

            "hotel": {

                "id":
                    hotel.id,

                "name":
                    hotel.name,

                "location":
                    hotel.location,

                "price":
                    float(hotel.price),

                "image_url":
                    hotel.image_url,

                "phone":
                    hotel.phone,

                "description":
                    hotel.description,

                "amenities":
                    hotel.amenities,

                "available_rooms":
                    hotel.available_rooms,

                "rating":
                    float(hotel.rating)
            }

        })

    except json.JSONDecodeError:

        return JsonResponse(
            {
                "error":
                    "Invalid JSON data."
            },
            status=400
        )

    except Exception as error:

        return JsonResponse(
            {
                "error":
                    str(error)
            },
            status=400
        )


# ============================================================
# DELETE HOTEL
# ============================================================

@csrf_exempt
def delete_hotel(request, hotel_id):

    if request.method != "DELETE":

        return JsonResponse(
            {
                "error":
                    "Only DELETE requests are allowed."
            },
            status=405
        )

    try:

        hotel = get_object_or_404(
            Hotel,
            id=hotel_id
        )

        # Do not delete a hotel if it has bookings.
        # This protects existing customer booking records.
        booking_count = Booking.objects.filter(
            hotel=hotel
        ).count()

        if booking_count > 0:

            return JsonResponse(
                {
                    "error":
                        "This hotel cannot be deleted because it has existing bookings."
                },
                status=400
            )

        hotel_name = hotel.name

        hotel.delete()

        return JsonResponse(
            {
                "message":
                    "Hotel deleted successfully.",

                "hotel":
                    hotel_name
            }
        )

    except Exception as error:

        return JsonResponse(
            {
                "error":
                    str(error)
            },
            status=400
        )


# ============================================================
# HOTEL DETAILS
# ============================================================

def hotel_detail(request, hotel_id):

    hotel = get_object_or_404(
        Hotel,
        id=hotel_id
    )

    check_in = request.GET.get(
        "check_in",
        ""
    ).strip()

    check_out = request.GET.get(
        "check_out",
        ""
    ).strip()

    available_rooms = get_available_rooms(
        hotel,
        check_in,
        check_out
    )

    return JsonResponse({

        "id":
            hotel.id,

        "name":
            hotel.name,

        "location":
            hotel.location,

        "price":
            float(hotel.price),

        "image_url":
            hotel.image_url,

        "phone":
            hotel.phone,

        "description":
            hotel.description,

        "amenities":
            hotel.amenities,

        "available_rooms":
            available_rooms,

        "total_rooms":
            hotel.available_rooms,

        "rating":
            float(hotel.rating),

        "source":
            "bond_desk",

        "bookable":
            available_rooms > 0
    })


# ============================================================
# CREATE BOOKING
# ============================================================

@csrf_exempt
def create_booking(request):

    if request.method != "POST":

        return JsonResponse(
            {
                "error":
                    "Only POST requests are allowed."
            },
            status=405
        )

    try:

        data = json.loads(
            request.body
        )

        hotel = get_object_or_404(
            Hotel,
            id=data.get("hotel_id")
        )

        rooms = int(
            data.get(
                "rooms",
                1
            )
        )

        guests = int(
            data.get(
                "guests",
                1
            )
        )

        check_in = data.get(
            "check_in"
        )

        check_out = data.get(
            "check_out"
        )

        customer_name = data.get(
            "customer_name",
            ""
        ).strip()

        customer_email = data.get(
            "customer_email",
            ""
        ).strip()

        customer_phone = data.get(
            "customer_phone",
            ""
        ).strip()

        # ----------------------------------------------------
        # BASIC VALIDATION
        # ----------------------------------------------------

        if not customer_name:

            return JsonResponse(
                {
                    "error":
                        "Customer name is required."
                },
                status=400
            )

        if not customer_email:

            return JsonResponse(
                {
                    "error":
                        "Customer email is required."
                },
                status=400
            )

        if not customer_phone:

            return JsonResponse(
                {
                    "error":
                        "Customer phone is required."
                },
                status=400
            )

        if rooms <= 0:

            return JsonResponse(
                {
                    "error":
                        "Invalid number of rooms."
                },
                status=400
            )

        if guests <= 0:

            return JsonResponse(
                {
                    "error":
                        "Invalid number of guests."
                },
                status=400
            )

        if not check_in or not check_out:

            return JsonResponse(
                {
                    "error":
                        "Check-in and check-out dates are required."
                },
                status=400
            )

        # ----------------------------------------------------
        # DATE VALIDATION
        # ----------------------------------------------------

        check_in_date = date.fromisoformat(
            check_in
        )

        check_out_date = date.fromisoformat(
            check_out
        )

        if check_in_date < date.today():

            return JsonResponse(
                {
                    "error":
                        "Check-in date cannot be in the past."
                },
                status=400
            )

        if check_out_date <= check_in_date:

            return JsonResponse(
                {
                    "error":
                        "Check-out must be after check-in."
                },
                status=400
            )

        # ----------------------------------------------------
        # CHECK ROOM AVAILABILITY
        # ----------------------------------------------------

        available_rooms = get_available_rooms(
            hotel,
            check_in,
            check_out
        )

        if rooms > available_rooms:

            return JsonResponse(
                {
                    "error":
                        f"Only {available_rooms} room(s) "
                        "are available for the selected dates."
                },
                status=400
            )

        # ----------------------------------------------------
        # CALCULATE TOTAL
        # ----------------------------------------------------

        nights = (
            check_out_date -
            check_in_date
        ).days

        total_amount = (
            hotel.price *
            nights *
            rooms
        )

        # ----------------------------------------------------
        # CREATE BOOKING
        # ----------------------------------------------------

        booking = Booking.objects.create(

            hotel=hotel,

            customer_name=customer_name,

            customer_email=customer_email,

            customer_phone=customer_phone,

            guests=guests,

            rooms=rooms,

            check_in=check_in_date,

            check_out=check_out_date,

            total_amount=total_amount
        )

        return JsonResponse(
            {

                "message":
                    "Booking confirmed successfully.",

                "booking_id":
                    booking.id,

                "hotel":
                    hotel.name,

                "nights":
                    nights,

                "rooms":
                    rooms,

                "remaining_rooms":
                    get_available_rooms(
                        hotel,
                        check_in,
                        check_out
                    ),

                "total_amount":
                    float(total_amount)
            },
            status=201
        )

    except ValueError:

        return JsonResponse(
            {
                "error":
                    "Invalid date or number format."
            },
            status=400
        )

    except Exception as error:

        return JsonResponse(
            {
                "error":
                    str(error)
            },
            status=400
        )


# ============================================================
# GET CUSTOMER BOOKINGS
# ============================================================

def get_bookings(request):

    customer_email = request.GET.get(
        "email",
        ""
    ).strip()

    if not customer_email:

        return JsonResponse(
            {
                "error":
                    "Customer email is required."
            },
            status=400
        )

    bookings = (
        Booking.objects
        .filter(
            customer_email__iexact=customer_email
        )
        .select_related("hotel")
        .order_by("-created_at")
    )

    data = []

    for booking in bookings:

        data.append({

            "id":
                booking.id,

            "hotel_name":
                booking.hotel.name,

            "hotel_location":
                booking.hotel.location,

            "customer_name":
                booking.customer_name,

            "customer_email":
                booking.customer_email,

            "customer_phone":
                booking.customer_phone,

            "guests":
                booking.guests,

            "rooms":
                booking.rooms,

            "check_in":
                booking.check_in.strftime(
                    "%Y-%m-%d"
                ),

            "check_out":
                booking.check_out.strftime(
                    "%Y-%m-%d"
                ),

            "total_amount":
                float(
                    booking.total_amount
                ),

            "created_at":
                booking.created_at.strftime(
                    "%d %b %Y, %I:%M %p"
                )
        })

    return JsonResponse(
        data,
        safe=False
    )