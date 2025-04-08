import json

import stripe
from django.http import JsonResponse
from django.views.generic import ListView, DetailView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone

from site_event import settings
from .models import Event, Ticket, Order, OrderTicket
from decimal import Decimal

stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

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
                total += ticket.prix * qty

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

def payment_view(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if order.status == 'paid':
        return redirect('order_confirmation', order_id=order.id)

    # Calcul du montant total de la commande
    amount = int(order.total_price * 100)  # Stripe prend des montants en centimes

    if request.method == 'POST':
        try:
            # Création d'un paiement
            intent = stripe.PaymentIntent.create(
                amount=amount,
                currency='eur',
                metadata={'order_id': order.id},
            )
            return JsonResponse({
                'clientSecret': intent.client_secret
            })
        except stripe.error.CardError as e:
            return JsonResponse({'error': str(e)})

    return render(request, 'event/payment_form.html', {'order': order, 'client_secret': None})

# views.py

def process_payment(request):
    if request.method == 'POST':
        # Charge les données JSON envoyées dans le corps de la requête
        data = json.loads(request.body)
        token = data.get('token')
        order_id = data.get('order_id')

        # Récupère la commande
        order = get_object_or_404(Order, id=order_id, user=request.user)

        try:
            # Crée un paiement avec le token Stripe
            intent = stripe.PaymentIntent.confirm(
                token,
                {
                    'payment_method': token,
                }
            )

            # Si le paiement est réussi
            if intent.status == 'succeeded':
                order.status = 'paid'
                order.save()
                return JsonResponse({'success': True})  # Retourne un JSON de succès
            else:
                return JsonResponse({'error': 'Le paiement a échoué.'})  # En cas d'échec du paiement

        except stripe.error.StripeError as e:
            return JsonResponse({'error': str(e)})  # En cas d'erreur Stripe

    else:
        # Si la méthode n'est pas POST, retourne une erreur 405 (Méthode non autorisée)
        return JsonResponse({'error': 'Méthode de requête non autorisée.'}, status=405)

def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if order.status == 'paid':
        return render(request, 'event/order_confirmation.html', {'order': order})
    else:
        return redirect('order_list')
