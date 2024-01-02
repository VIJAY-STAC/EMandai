from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(B2BOrders)
class B2BOrdersAdmin(admin.ModelAdmin):
    list_display = [field.name for field in B2BOrders._meta.fields]

@admin.register(B2COrders)
class B2COrdersAdmin(admin.ModelAdmin):
    list_display = [field.name for field in B2COrders._meta.fields]


@admin.register(OrderProducts)
class OrderProductsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in OrderProducts._meta.fields]

@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Cart._meta.fields]