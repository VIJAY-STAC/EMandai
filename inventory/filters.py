import django_filters
from django_filters import rest_framework as filters
from django.db.models import Q
from .models import *

class ProductsFilter(django_filters.FilterSet):
    p_name = django_filters.CharFilter(method="serach_products")
    cat = django_filters.CharFilter(method="serach_cat")

    class Meta:
        model = Products
        fields = [  "name",
                    "product_images",
                    "description",
                    "category",
                 ]

    def serach_products(self, queryset, name, value):
        queryset= queryset.filter(name__icontains=value)
        return queryset
    
    def serach_cat(self, queryset, name, value):
        queryset= queryset.filter(category__name__icontains=value)
        return queryset

class CategoryFilter(django_filters.FilterSet):
    cat = django_filters.CharFilter(method="serach_category")
    class Meta:
        model = Category

        fields = [  "name"    ]

    def serach_category(self, queryset, name, value):
        queryset= queryset.filter(name__icontains=value)
        return queryset


class ProductsStockFilter(django_filters.FilterSet):
    p_name = filters.CharFilter(method="search_products")
    cat = filters.CharFilter(method="search_category")

    class Meta:
        model = ProductsStock
        fields = ["available"]

    def search_products(self, queryset, name, value):
        if value:
            queryset = queryset.filter(product__name__icontains=value)
        return queryset

    def search_category(self, queryset, name, value):
        if value:
            queryset = queryset.filter(product__category__name__icontains=value)
        return queryset
