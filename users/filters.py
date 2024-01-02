import django_filters
from django_filters import rest_framework as filters

from .models import *

class UserFilter(django_filters.FilterSet):
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name','last_name','address','pincode','gender','user_type','phone_number','username',
                 'date_of_birth', ]
