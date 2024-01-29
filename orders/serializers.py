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
    invoice_number = serializers.CharField(required=False)
    customer_status= serializers.CharField(required=False)
    class Meta:
        model = B2COrders
        fields=(
            "id",
            "invoice_number",
            "created_at",
            "order_type",
            "amount",
            "status",
            "customer_status",
            "payment_type",
            "payment_status",
            "quadrant"
        )

class B2COrderRetrivewSerializer(serializers.ModelSerializer):
    invoice_number = serializers.CharField(required=False)
    products = serializers.SerializerMethodField(default=None)
    class Meta:
        model = B2COrders
        fields=(
            "id",
            "invoice_number",
            "created_at",
            "order_type",
            "amount",
            "status",
            "customer_status",
            "payment_type",
            "payment_status",
            "quadrant",
            "products"
        )
    def get_products(self, obj):
        o_ps = OrderProducts.objects.filter(b2corder_id=obj.id)
        res = []
        for o_p in o_ps:
            data = {
                "id": o_p.id,
                "product": o_p.b2cproduct.id,
                "quantity": o_p.quantity,
                "amt":o_p.amt,
                "total_amt": o_p.total_amt,
                "product_name": o_p.b2cproduct.product.name,
                "packaging": o_p.b2cproduct.product.packaging,
                "product_images":  o_p.b2cproduct.product.product_images.all().first().url,
                "discount": o_p.discount
            }
            res.append(data)
        return res

class CartSerializer(serializers.ModelSerializer):
    product_name= serializers.CharField(source="product.product.name")
    available = serializers.BooleanField(source="product.available")
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
            "available"
        )

    def get_product_images(self, obj):
        img = obj.product.product.product_images.all().first().url
        return img

