from .models import *

class ProductsQueryset:
    def custom_get_queryset(self):
        queryset = Products.objects.select_related("category").all("-created_at")
        return queryset