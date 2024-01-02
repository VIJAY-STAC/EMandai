from django.contrib import admin
from .models import *

# Register your models here.

@admin.register(File)
class FilerdersAdmin(admin.ModelAdmin):
    list_display = [field.name for field in File._meta.fields]



@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Category._meta.fields]



@admin.register(Products)
class ProductsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in Products._meta.fields]



@admin.register(ProductsStock)
class ProductsStockAdmin(admin.ModelAdmin):
    list_display = [field.name for field in ProductsStock._meta.fields]

@admin.register(FarmerProducts)
class FarmerProductsAdmin(admin.ModelAdmin):
    list_display = [field.name for field in FarmerProducts._meta.fields]