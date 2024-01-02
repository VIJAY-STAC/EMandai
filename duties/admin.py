from django.contrib import admin
from .models import *
# Register your models here.

@admin.register(Quadrants)
class OrderProductsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Quadrants._meta.fields]


@admin.register(Routes)
class OrderProductsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Routes._meta.fields]


@admin.register(Duty)
class OrderProductsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Duty._meta.fields]