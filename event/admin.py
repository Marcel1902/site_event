from django.contrib import admin
from .models import Event, Order, OrderTicket, Ticket
# Register your models here.

admin.site.register(Event)
admin.site.register(Order)
admin.site.register(OrderTicket)
admin.site.register(Ticket)
