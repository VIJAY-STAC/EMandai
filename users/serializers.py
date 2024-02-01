from rest_framework import serializers
from .models import User
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group

class UserSerializer(serializers.ModelSerializer):
   
    class Meta:
        model = User
        fields = (  'id',
                    'email',
                    'first_name',
                    'last_name',
                    'address',
                    'pincode',
                    'quadrant',
                    'gender',
                    'user_type',
                    'phone_number',
                    'username',
                    'date_of_birth',
                    'latitude',
                    'longitude'
                
                )

        extra_kwargs = {
            'latitude': {'required': False},
            'longitude': {'required': False},
        }
     

class UserRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ("id", "name")