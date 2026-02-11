from django.db import models

from django.contrib.auth.models import User
from foodiesapp.models import FoodItem
# Create your models here.

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    ordered_at = models.DateTimeField(auto_now_add=True)
    address = models.TextField()
    total_amount = models.DecimalField(max_digits=8, decimal_places=2)
    phone = models.CharField(max_length=15)
    reference = models.CharField(max_length=64, blank=True, null=True, unique=True)
    status = models.CharField(max_length=50, choices=[('Pending', 'Pending'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled' )], default='Pending')

    def __str__(self):
        return f"Order of {self.quantity} x {self.food_item.name} by {self.user.username}"
    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    food_item = models.ForeignKey(FoodItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return f"{self.quantity} x {self.food_item.name} in Order {self.order.id}"