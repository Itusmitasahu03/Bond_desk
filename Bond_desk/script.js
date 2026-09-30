// ========================================
// BOND_DESK - SCRIPT.JS
// ========================================


// ========================================
// SEARCH HOTELS FROM DJANGO + OPENSTREETMAP
// ========================================

async function searchHotels() {

    const locationInput =
        document.getElementById("locationInput");

    if (!locationInput) {
        console.error("locationInput not found.");
        return;
    }

    const location =
        locationInput.value.trim();

    if (location === "") {

        alert("Please enter a location.");

        locationInput.focus();

        return;
    }


    // ========================================
    // GET DATES
    // ========================================

    const checkInInput =
        document.getElementById("checkIn");

    const checkOutInput =
        document.getElementById("checkOut");

    const checkIn =
        checkInInput
            ? checkInInput.value
            : "";

    const checkOut =
        checkOutInput
            ? checkOutInput.value
            : "";


    // ========================================
    // VALIDATE DATES
    // ========================================

    if (checkIn && checkOut) {

        if (checkOut <= checkIn) {

            alert(
                "Check-out date must be after check-in date."
            );

            return;
        }
    }


    // ========================================
    // HOTEL RESULTS SECTION
    // ========================================

    const hotelSection =
        document.getElementById("hotels");


    // ========================================
    // LOADING MESSAGE
    // ========================================

    if (hotelSection) {

        hotelSection.innerHTML = `

            <div class="search-loading">

                <i class="fas fa-spinner fa-spin"></i>

                <h3>
                    Searching hotels...
                </h3>

                <p>
                    Finding hotels in
                    <strong>${location}</strong>
                </p>

            </div>

        `;

        hotelSection.scrollIntoView({
            behavior: "smooth"
        });
    }


    // ========================================
    // SEARCH DJANGO
    // ========================================

    try {

        let apiUrl =
            "http://127.0.0.1:8000/api/search-anywhere/?location="
            + encodeURIComponent(location);


        // Add check-in date

        if (checkIn) {

            apiUrl +=
                "&check_in="
                + encodeURIComponent(checkIn);

        }


        // Add check-out date

        if (checkOut) {

            apiUrl +=
                "&check_out="
                + encodeURIComponent(checkOut);

        }


        console.log(
            "Searching:",
            apiUrl
        );


        const response =
            await fetch(apiUrl);


        if (!response.ok) {

            throw new Error(
                "Django API returned status "
                + response.status
            );

        }


        const hotels =
            await response.json();


        console.log(
            "Hotels received:",
            hotels
        );


        // ========================================
        // NO RESULTS
        // ========================================

        if (
            !Array.isArray(hotels)
            ||
            hotels.length === 0
        ) {

            if (hotelSection) {

                hotelSection.innerHTML = `

                    <div class="search-loading">

                        <i class="fas fa-hotel"></i>

                        <h3>
                            No hotels found
                        </h3>

                        <p>
                            We could not find hotels in
                            <strong>${location}</strong>.
                        </p>

                    </div>

                `;

            }

            return;
        }


        // ========================================
        // CREATE HOTEL CARDS
        // ========================================

        let hotelHTML = "";


        hotels.forEach(function (hotel) {


            // ====================================
            // RATING
            // ====================================

            let ratingHTML = "";


            if (
                hotel.rating
                &&
                Number(hotel.rating) > 0
            ) {

                ratingHTML = `

                    <span class="hotel-rating">

                        <i class="fas fa-star"></i>

                        ${hotel.rating}

                    </span>

                `;

            }


            // ====================================
            // PRICE
            // ====================================

            let priceHTML = "";


            if (
                hotel.source === "bond_desk"
                &&
                hotel.price !== null
                &&
                hotel.price !== undefined
            ) {

                priceHTML = `

                    <div class="hotel-price">

                        <strong>
                            ₹${hotel.price}
                        </strong>

                        <span>
                            / night
                        </span>

                    </div>

                `;

            }

            else {

                priceHTML = `

                    <div class="hotel-price">

                        <strong>
                            Price unavailable
                        </strong>

                        <span>
                            External listing
                        </span>

                    </div>

                `;

            }


            // ====================================
            // AVAILABILITY
            // ====================================

            let availabilityHTML = "";


            if (
                hotel.source === "bond_desk"
            ) {

                if (
                    hotel.bookable === true
                    &&
                    Number(hotel.available_rooms) > 0
                ) {

                    availabilityHTML = `

                        <div class="hotel-availability available">

                            <i class="fas fa-circle-check"></i>

                            <strong>
                                ${hotel.available_rooms}
                            </strong>

                            room(s) available

                        </div>

                    `;

                }

                else {

                    availabilityHTML = `

                        <div class="hotel-availability unavailable">

                            <i class="fas fa-circle-xmark"></i>

                            No rooms available
                            for selected dates

                        </div>

                    `;

                }

            }

            else {

                availabilityHTML = `

                    <div class="hotel-availability external">

                        <i class="fas fa-location-dot"></i>

                        External hotel listing

                    </div>

                `;

            }


            // ====================================
            // BUTTON
            // ====================================

            let buttonHTML = "";


            if (
                hotel.source === "bond_desk"
                &&
                hotel.bookable === true
                &&
                hotel.id
            ) {

                buttonHTML = `

                    <button
                        class="book-btn"
                        onclick="bookHotel(${hotel.id})">

                        <i class="fas fa-calendar-check"></i>

                        View & Book

                    </button>

                `;

            }

            else if (
                hotel.source === "bond_desk"
                &&
                hotel.bookable === false
            ) {

                buttonHTML = `

                    <button
                        class="book-btn"
                        disabled>

                        <i class="fas fa-ban"></i>

                        Not Available

                    </button>

                `;

            }

            else if (
                hotel.map_url
            ) {

                buttonHTML = `

                    <a
                        class="book-btn"
                        href="${hotel.map_url}"
                        target="_blank"
                        rel="noopener noreferrer">

                        <i class="fas fa-location-dot"></i>

                        View Location

                    </a>

                `;

            }

            else {

                buttonHTML = `

                    <button
                        class="book-btn"
                        disabled>

                        Location unavailable

                    </button>

                `;

            }


            // ====================================
            // PHONE
            // ====================================

            let phoneHTML = "";


            if (
                hotel.phone
                &&
                hotel.phone !== "Not available"
            ) {

                phoneHTML = `

                    <span>

                        <i class="fas fa-phone"></i>

                        ${hotel.phone}

                    </span>

                `;

            }


            // ====================================
            // WEBSITE
            // ====================================

            let websiteHTML = "";


            if (hotel.website) {

                websiteHTML = `

                    <a
                        href="${hotel.website}"
                        target="_blank"
                        rel="noopener noreferrer">

                        <i class="fas fa-globe"></i>

                        Website

                    </a>

                `;

            }


            // ====================================
            // HOTEL CARD
            // ====================================

            hotelHTML += `

                <div class="hotel-card">


                    <!-- HOTEL IMAGE -->

                    <div class="hotel-image-container">

                        <img
                            src="${hotel.image_url}"
                            alt="${hotel.name}"
                            loading="lazy"

                            onerror="
                                this.src='https://images.unsplash.com/photo-1566073771259-6a8506099945?auto=format&fit=crop&w=1000&q=80';
                            "
                        >

                        ${ratingHTML}

                    </div>


                    <!-- HOTEL CONTENT -->

                    <div class="hotel-card-content">


                        <!-- NAME -->

                        <h3>
                            ${hotel.name}
                        </h3>


                        <!-- LOCATION -->

                        <p class="location">

                            <i class="fas fa-location-dot"></i>

                            ${hotel.location || location}

                        </p>


                        <!-- DESCRIPTION -->

                        <p class="hotel-description">

                            ${
                                hotel.description
                                ||
                                "Hotel information available."
                            }

                        </p>


                        <!-- AMENITIES -->

                        <div class="hotel-amenities">

                            <span>

                                <i class="fas fa-hotel"></i>

                                ${
                                    hotel.amenities
                                    ||
                                    "Hotel"
                                }

                            </span>

                            ${phoneHTML}

                            ${websiteHTML}

                        </div>


                        <!-- AVAILABILITY -->

                        ${availabilityHTML}


                        <!-- BOTTOM -->

                        <div class="hotel-bottom">

                            ${priceHTML}

                            ${buttonHTML}

                        </div>


                    </div>

                </div>

            `;

        });


        // ========================================
        // DISPLAY RESULTS
        // ========================================

        if (hotelSection) {

            let dateMessage = "";


            if (checkIn && checkOut) {

                dateMessage = `

                    <p class="search-date-info">

                        Availability for

                        <strong>
                            ${checkIn}
                        </strong>

                        to

                        <strong>
                            ${checkOut}
                        </strong>

                    </p>

                `;

            }


            hotelSection.innerHTML = `

                <div class="search-results-header">

                    <h2>
                        Hotels in ${location}
                    </h2>

                    <p>

                        ${hotels.length}

                        hotel(s) found

                    </p>

                    ${dateMessage}

                </div>


                <div class="hotel-grid">

                    ${hotelHTML}

                </div>


                <p class="osm-attribution">

                    Location data ©

                    <a
                        href="https://www.openstreetmap.org/copyright"
                        target="_blank"
                        rel="noopener noreferrer">

                        OpenStreetMap contributors

                    </a>

                </p>

            `;


            hotelSection.scrollIntoView({
                behavior: "smooth"
            });

        }


    }

    // ========================================
    // ERROR
    // ========================================

    catch (error) {

        console.error(
            "Hotel search error:",
            error
        );


        if (hotelSection) {

            hotelSection.innerHTML = `

                <div class="search-loading">

                    <i class="fas fa-triangle-exclamation"></i>

                    <h3>
                        Unable to search hotels
                    </h3>

                    <p>
                        Please make sure Django is running.
                    </p>

                    <p>

                        Django API:

                        <strong>
                            127.0.0.1:8000
                        </strong>

                    </p>

                </div>

            `;

        }

    }

}


// ========================================
// BOOK HOTEL
// ========================================

function bookHotel(hotelId) {

    if (!hotelId) {

        alert(
            "Hotel information is missing."
        );

        return;
    }


    // Keep the selected dates
    // while opening booking page

    const checkIn =
        document.getElementById("checkIn");

    const checkOut =
        document.getElementById("checkOut");


    let url =
        "booking.html?id="
        + encodeURIComponent(hotelId);


    if (
        checkIn
        &&
        checkIn.value
    ) {

        url +=
            "&check_in="
            + encodeURIComponent(
                checkIn.value
            );

    }


    if (
        checkOut
        &&
        checkOut.value
    ) {

        url +=
            "&check_out="
            + encodeURIComponent(
                checkOut.value
            );

    }


    window.location.href = url;

}


// ========================================
// RESET HOTEL SEARCH
// ========================================

function resetHotels() {

    const hotelCards =
        document.querySelectorAll(
            ".hotel-card"
        );


    hotelCards.forEach(
        function (card) {

            card.style.display =
                "block";

        }
    );

}


// ========================================
// PAGE INITIALIZATION
// ========================================

document.addEventListener(
    "DOMContentLoaded",
    function () {


        // ====================================
        // SEARCH BUTTON
        // ====================================

        const searchButton =
            document.querySelector(
                ".search-btn"
            );


        if (searchButton) {

            searchButton.addEventListener(
                "click",
                function (event) {

                    event.preventDefault();

                    searchHotels();

                }
            );

        }


        // ====================================
        // ENTER KEY SEARCH
        // ====================================

        const locationInput =
            document.getElementById(
                "locationInput"
            );


        if (locationInput) {

            locationInput.addEventListener(
                "keypress",
                function (event) {

                    if (
                        event.key === "Enter"
                    ) {

                        event.preventDefault();

                        searchHotels();

                    }

                }
            );

        }


        // ====================================
        // CHECK-IN / CHECK-OUT
        // ====================================

        const checkIn =
            document.getElementById(
                "checkIn"
            );


        const checkOut =
            document.getElementById(
                "checkOut"
            );


        if (
            checkIn
            &&
            checkOut
        ) {

            checkIn.addEventListener(
                "change",
                function () {

                    checkOut.min =
                        checkIn.value;


                    if (
                        checkOut.value
                        &&
                        checkOut.value <
                        checkIn.value
                    ) {

                        checkOut.value = "";

                    }

                }
            );

        }


        // ====================================
        // TODAY'S DATE
        // ====================================

        const today =
            new Date()
                .toISOString()
                .split("T")[0];


        if (checkIn) {

            checkIn.min =
                today;

        }


        if (checkOut) {

            checkOut.min =
                today;

        }


        // ====================================
        // VIEW HOTEL BUTTONS
        // ====================================

        const viewButtons =
            document.querySelectorAll(
                ".view-btn"
            );


        viewButtons.forEach(
            function (button) {

                button.addEventListener(
                    "click",
                    function (event) {

                        event.preventDefault();


                        const hotelCard =
                            this.closest(
                                ".hotel-card"
                            );


                        if (!hotelCard) {

                            return;

                        }


                        const hotelNameElement =
                            hotelCard.querySelector(
                                "h3"
                            );


                        const hotelName =
                            hotelNameElement
                                ? hotelNameElement.innerText
                                : "Hotel";


                        alert(

                            "Opening details for "
                            +
                            hotelName
                            +
                            "..."

                        );

                    }
                );

            }
        );

    }
);