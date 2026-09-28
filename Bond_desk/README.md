# Bond_Desk

Bond_Desk is a Django + SQLite hotel search and booking project.

## Frontend
Open the frontend pages with VS Code Live Server:
- index.html
- customer.html
- login.html
- dashboard.html
- booking.html
- admin/admin_dashboard.html

## Backend
Open PowerShell in the `backend` folder.

Activate your virtual environment if needed, then install:
    pip install -r requirements.txt

Run:
    python manage.py migrate
    python manage.py runserver

Django API:
    http://127.0.0.1:8000/api/search/?location=Bhubaneswar

## Search
The backend search is word-based. A hotel can store a full location such as:
"CDA Sector 6, Cuttack, Odisha"

Searches such as:
- Cuttack
- CDA
- Sector 6
- CDA 6 Cuttack

can match the stored hotel information.

## Booking
Dashboard -> Search -> View & Book -> Confirm Booking.

Bookings are stored in SQLite and available rooms are reduced after a successful booking.

## Important
The included `venv` is intentionally not included in the final ZIP. Create/use your own virtual environment and install the requirements.
