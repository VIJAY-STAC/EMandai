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
            "order_type",
            "amount",
            "status",
            "payment_type",
            "payment_status",
            "quadrant"
        )
