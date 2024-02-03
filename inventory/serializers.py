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


class CategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields=(
            "name",
        )
    def create(self, validated_data):
        return Category.objects.create(**validated_data)

class CategorySerializer(serializers.ModelSerializer):
    cat_images = serializers.SerializerMethodField(default=None)
    class Meta:
        model = Category
        fields=(
            "id",
            "name",
            "cat_images"
        )

    def get_cat_images(self, obj):
        img = obj.images.all().first().url  if obj.images.all().first() else None
        return img


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


class ProductsStockSerializer(serializers.ModelSerializer):
     class Meta:
        model = ProductsStock
        fields=(
            	"product",
                "sale_mrp",
                "expiry_date",
                "inventory",
                "available",
                "discount"
        )


class ProductsStockListSerializer(serializers.ModelSerializer):
    product_name= serializers.CharField(source="product.name")
    packaging = serializers.CharField(source="product.packaging")
    product_images = serializers.SerializerMethodField(default=None)
    category=serializers.CharField(source="product.category.name")
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
            "discount",
            "product_images",
            "category"
        )
    def get_product_images(self, obj):
        img = obj.product.product_images.all().first().url
        return img