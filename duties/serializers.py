
from rest_framework import serializers


from .models import *


class RoutesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routes
        fields=(
            "id",
            "name",
            "pincode",
            "quadrant",
            "areas",
            "is_active"
        )

class RoutesListSerializer(serializers.ModelSerializer):
    quadrant = serializers.CharField(source="quadrant.name", default="")
    class Meta:
        model = Routes
        fields=(
            "id",
            "name",
            "pincode",
            "quadrant",
            "areas",
            "is_active"
        )

class QuadrantsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Quadrants
        fields=(
            "id",
            "name",
            "is_active"
        )

# DutySeriaizer

class DutySerializer(serializers.ModelSerializer):
    class Meta:
        model = Duty
        fields=(
            "id",
            "name",
            "started_at",
            "completed_at",
            "status",
            "total_outlets",
            "delivered_attempted_outlets",
            "quadrant",
            "rider"
        )

class DutyListSerializer(serializers.ModelSerializer):
    quadrant_name = serializers.CharField(source="quadrant.name", default="")
    rider = serializers.CharField(source="rider.full_name", default="")
    class Meta:
        model = Duty
        fields=(
            "id",
            "name",
            "started_at",
            "completed_at",
            "status",
            "total_outlets",
            "delivered_attempted_outlets",
            "quadrant",
            "quadrant_name",
            "rider"
        )