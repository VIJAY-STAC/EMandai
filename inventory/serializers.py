from rest_framework import serializers

from .models import *

class ProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Products
        fields=(
            "id",
            "name",
            "description",
            "category",
            "packaging"
        )
class ProductsListSerializer(serializers.ModelSerializer):
    category = serializers.CharField(source="category.name")
    class Meta:
        model = Products
        fields=(
            "id",
            "name",
            "product_images",
            "description",
            "category",
            "packaging"
        )

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields=(
            "id",
            "name",
        )

class FarmerProductsSerializer(serializers.ModelSerializer):
    class Meta:
        model = FarmerProducts
        fields=(
            "product",
            "mrp",
            "expiry_date",
            "packaging",
            "quantity",
            "farmer",
            
        )

class FarmerProductsListSerializer(serializers.ModelSerializer):
    product_name= serializers.CharField(source="product.name")
    farmer_name= serializers.CharField(source="farmer.full_name")
    class Meta:
        model = FarmerProducts
        fields=(
            "id",
            "product",
            "product_name",
            "mrp",
            "expiry_date",
            "packaging",
            "quantity",
            "farmer",
            "farmer_name"
        )

ProductsStock


class ProductsStockListSerializer(serializers.ModelSerializer):
    product_name= serializers.CharField(source="product.name")
    packaging = serializers.CharField(source="product.packaging")
    class Meta:
        model = ProductsStock
        fields=(
            "id",
            "product",
            "product_name",
            "sale_mrp",
            "expiry_date",
            "packaging",
            "inventory",
            "available",
            "discount"
        )