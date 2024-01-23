from rest_framework import serializers


from .models import *

class B2BOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2BOrders
        fields=(
            "id",
            "order_type",
            "amount",
            "status",
            "payment_type",
            "order_to",
         
        )

class B2BOrderListSerializer(serializers.ModelSerializer):
    order = serializers.CharField(source="order_to.full_name")
    class Meta:
        model = B2BOrders
        fields=(
            "id",
            "order_type",
            "amount",
            "status",
            "payment_type",
            "payment_status",
            "order"
        )


class B2COrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = B2COrders
        fields=(
            "id",
            "created_at",
            "order_type",
            "amount",
            "status",
            "payment_type",
            "payment_status",
            "quadrant"
        )

class CartSerializer(serializers.ModelSerializer):
    product_name= serializers.CharField(source="product.product.name")
    packaging = serializers.CharField(source="product.product.packaging")
    product_images = serializers.SerializerMethodField(default=None)
    discount = serializers.CharField(source="product.discount", default=0)
    class Meta:
        model = Cart
        fields =(
            "id",
            "product",
            "quantity",
            "amt",
            "total_amt",
            "product_name",
            "packaging",
            "product_images",
            "discount",
        )

    def get_product_images(self, obj):
        img = obj.product.product.product_images.all().first().url
        return img

