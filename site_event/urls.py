
from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from event import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.EventListView.as_view(), name='event_list'),
    path('event/<int:pk>/', views.EventDetailView.as_view(), name='event_detail'),
    path('order/<int:event_id>/', views.order_tickets, name='order_tickets'),
    path('payment/<int:order_id>/', views.payment_view, name='payment_view'),
    path('process_payment/', views.process_payment, name='process_payment'),
    path('order_confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('my-orders/', views.MyOrdersView.as_view(), name='my_orders'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
