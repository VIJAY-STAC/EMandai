from .models import *

class ProductsQueryset:
    def custom_get_queryset(self):
        queryset = Products.objects.select_related("category").all("-created_at")
        return queryset

class ProductsStockQueryset:
    def custom_get_queryset(self):
        if self.action =="list":
            queryset = ProductsStock.objects.select_related("product", "product__category").order_by("-created_at")
        return queryset