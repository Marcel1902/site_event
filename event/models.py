from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateTimeField()
    location = models.CharField(max_length=200)
    image = models.ImageField(upload_to='event_images/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title



class Ticket(models.Model):
    event = models.ForeignKey(Event, related_name="tickets", on_delete=models.CASCADE)
    ticket_type = models.CharField(max_length=50)
    prix = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()

    def __str__(self):
        return f"ticket {self.ticket_type} pour {self.event.title}"

    @property
    def available_quantity(self):
        sold = sum(item.quantity for item in self.orderticket_set.all())
        return self.quantity - sold


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    tickets = models.ManyToManyField(Ticket, through='OrderTicket')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('paid', 'Paid')])

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"

class OrderTicket(models.Model):
    order = models.ForeignKey('Order', on_delete=models.CASCADE)
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.ticket.ticket_type} (Order {self.order.id})"
