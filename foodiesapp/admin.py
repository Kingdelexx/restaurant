from django.contrib import admin
from .models import Category, FoodItem, Profile
# Register your models here.

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)

class FoodItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'created_at')
    list_filter = ('category',)
    search_fields = ('name', 'description')

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'phone', 'address')
    search_fields = ('user__username', 'phone')

admin.site.register(Category, CategoryAdmin)
admin.site.register(FoodItem, FoodItemAdmin)
admin.site.register(Profile, ProfileAdmin)