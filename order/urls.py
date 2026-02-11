from django.urls import path
from . import views


urlpatterns = [
    path('create/', views.create_order, name='create_order'),
    path('details/<int:order_id>/', views.order_details, name='order_details'),
]