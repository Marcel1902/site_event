from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from .models import Event, Ticket, Order, OrderTicket
from decimal import Decimal


# Create your views here.
class EventListView(ListView):
    model = Event
    template_name = 'event/event_list.html'
    context_object_name = 'events'

class EventDetailView(DetailView):
    model = Event
    template_name = 'event/event_detail.html'
    context_object_name = 'event'


@login_required
def order_tickets(request, event_id):
    event = get_object_or_404(Event, pk=event_id)

    if request.method == 'POST':
        total = Decimal(0)
        order = Order.objects.create(user=request.user, event=event, total_price=0, status='pending')

        for ticket in event.tickets.all():
            qty = int(request.POST.get(f'ticket_{ticket.id}', 0))
            if qty > 0 and qty <= ticket.available_quantity:
                OrderTicket.objects.create(order=order, ticket=ticket, quantity=qty)
                total += ticket.price * qty

        order.total_price = total
        order.save()
        return redirect('my_orders')  # À adapter selon tes URLs

    return render(request, 'event/order_form.html', {'event': event})

class MyOrdersView(LoginRequiredMixin, ListView):
    model = Order
    template_name = 'event/my_orders.html'
    context_object_name = 'orders'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-order_date')