from django.db import models


# ============================================================
# HOTEL MODEL
# ============================================================

class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=300)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    amenities = models.TextField(blank=True, null=True)

    available_rooms = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        default=0
    )

    def __str__(self):
        return self.name


# ============================================================
# BOOKING MODEL
# ============================================================

class Booking(models.Model):
    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE,
        related_name="bookings"
    )

    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_phone = models.CharField(max_length=30)

    check_in = models.DateField()
    check_out = models.DateField()

    rooms = models.PositiveIntegerField(default=1)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.customer_name} - {self.hotel.name}"


# ============================================================
# JOB MODEL
# ============================================================

class Job(models.Model):

    JOB_TYPES = [
        ("Online Job", "Online Job"),
        ("Nearby Job", "Nearby Job"),
        ("Work From Home", "Work From Home"),
        ("Part Time Job", "Part Time Job"),
        ("Full Time Job", "Full Time Job"),
    ]

    title = models.CharField(max_length=200)

    company = models.CharField(max_length=200)

    location = models.CharField(max_length=200)

    job_type = models.CharField(
        max_length=50,
        choices=JOB_TYPES
    )

    work_mode = models.CharField(
        max_length=100,
        blank=True
    )

    salary = models.CharField(
        max_length=100,
        blank=True
    )

    skills = models.CharField(
        max_length=500,
        blank=True
    )

    description = models.TextField(
        blank=True
    )

    application_link = models.URLField(
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.title} - {self.location}"