
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from event.views import (
    EventListView, EventDetailView, order_tickets, MyOrdersView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', EventDetailView.as_view(), name='event_detail'),
    path('event/<int:event_id>/order/', order_tickets, name='order_tickets'),
    path('my-orders/', MyOrdersView.as_view(), name='my_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
