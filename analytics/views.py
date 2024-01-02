from datetime import datetime
import json
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from inventory.models import ProductsStock, FarmerProducts

from .models import *
from .serializers import * 
# Create your views here.

class B2BOrdersViewSet(viewsets.ModelViewSet):
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)