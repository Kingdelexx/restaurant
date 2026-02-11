from django.urls import path
from . import views


urlpatterns = [
    path('', views.index, name='index'),
    path('food_item/<int:pk>/', views.food_item, name='food_item'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_detail, name='profile'),
    path('profile/update/', views.profile_update, name='profile_update'),
    path('cart/<int:food_item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:food_item_id>/', views.remove_cart, name='remove_cart'),
    path('cart/', views.cart_view, name='cart_view'),
    path('checkout/', views.checkout, name='checkout'),
    path('create/', views.create_food_item, name='create_food_item'),
]