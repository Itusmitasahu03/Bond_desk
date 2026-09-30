from django.db import models


class Hotel(models.Model):
    name = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image_url = models.URLField()
    phone = models.CharField(max_length=20)
    description = models.TextField(blank=True)
    amenities = models.CharField(max_length=500, blank=True)
    available_rooms = models.IntegerField(default=0)
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=4.0)

    def __str__(self):
        return self.name

class Booking(models.Model):

    hotel = models.ForeignKey(
        Hotel,
        on_delete=models.CASCADE
    )

    customer_name = models.CharField(
        max_length=200
    )

    customer_email = models.EmailField()

    customer_phone = models.CharField(
        max_length=20
    )

    guests = models.IntegerField(
        default=1
    )

    rooms = models.IntegerField(
        default=1
    )

    check_in = models.DateField()

    check_out = models.DateField()

    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return (
            self.customer_name +
            " - " +
            self.hotel.name
        )