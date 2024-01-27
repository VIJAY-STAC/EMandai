from django.shortcuts import render
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
import base64
from django.utils import timezone

from .queryset import ProductsQueryset, ProductsStockQueryset
from .utils import product_image_upload
from .filters import *

from .serializers import *
from .models import *
# Create your views here.

class ProductsViewSet(viewsets.ModelViewSet, ProductsQueryset):
    model = Products
    serializer_class = ProductsListSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProductsFilter
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Products.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data= request.data
        serializer = ProductsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(created_by=request.user)

        PRODUCT_IMAGES_KEY = "product_images/{image_name}.jpeg"

        file = request.data.get("product_images")

        opened_file = file.open()
        base64_file = base64.b64encode(opened_file.read()).decode("utf-8")
        opened_file.close()
        key = PRODUCT_IMAGES_KEY.format(
            image_name=str(product.id)[24:]
            + "-"
            + str(int(timezone.now().timestamp()))
        )
        image_id = product_image_upload(
            product_id=str(product.id),
            base64_file=base64_file,
            key=key,
            file_name=str(file.name),
            file_type=file.content_type,
            file_size=file.size,
        )
        serializer= ProductsListSerializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Product=Products.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"error":"product does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = ProductsSerializer(Product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_product=serializer.save(last_modified_by=request.user)
        serializer=ProductsListSerializer(updated_product)
        return Response(serializer.data, status=status.HTTP_200_OK)



class CategoryViewSet(viewsets.ModelViewSet, ProductsQueryset):
    model = Category
    serializer_class = CategorySerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    filter_class = CategoryFilter
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Category.objects.all()
        return queryset


class FarmerProductsViewSet(viewsets.ModelViewSet, ProductsQueryset):
    model = FarmerProducts
    serializer_class = FarmerProductsListSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = FarmerProducts.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            return Response({"error": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN) 
        data= request.data
        data["farmer"]=request.user.id
        serializer = FarmerProductsSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        product = serializer.save(created_by=request.user)
        serializer = FarmerProductsListSerializer(product)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        Products=FarmerProducts.objects.all().order_by('-created_at')
        serializer=FarmerProductsListSerializer(Products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   

    @action(detail=False, methods=['get'])
    def farmer_product_list(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            return Response({"error": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        user_id = request.user.id
        Products=FarmerProducts.objects.filter(farmer_id=user_id).order_by('-created_at')
        serializer=FarmerProductsListSerializer(Products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)   

    def retrieve(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            return Response({"error": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        id = kwargs.get('pk')
        try:
            product=FarmerProducts.objects.get(id=id)
        except FarmerProducts.DoesNotExist:
            return Response({"error":"Product does not found with given id"},status=status.HTTP_400_BAD_REQUEST)
        serializer=FarmerProductsListSerializer(product)
        return Response(serializer.data, status=status.HTTP_200_OK)
       

    def update(self, request, *args, **kwargs):
        if request.user.user_type != 'farmer':
            return Response({"error": "You do not have permission to perform this action"}, status=status.HTTP_403_FORBIDDEN)
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            Product=FarmerProducts.objects.get(id=id)
        except Product.DoesNotExist:
            return Response({"error":"product does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = FarmerProductsSerializer(Product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_product=serializer.save(last_modified_by=request.user)
        serializer=FarmerProductsListSerializer(updated_product)
        return Response(serializer.data, status=status.HTTP_200_OK)

     
class ProductsStockViewSet(viewsets.ModelViewSet, ProductsStockQueryset):
    model = ProductsStock
    serializer_class = ProductsStockListSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    filter_class = ProductsStockFilter
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = self.custom_get_queryset()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializers = ProductsStockSerializer(data=data)
        serializers.is_valid(raise_exception=True)
        serializers.save()
        return Response(serializers.data, status=status.HTTP_200_OK)


    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        mrp =request.data.get('mrp', None)
        discount =request.data.get('discount',None)
        try:
            product_stock = ProductsStock.objects.get(id=id)
        except ProductsStock.DoesNotExist:
            return Response({"error":"product not present with given id"}, status=status.HTTP_400_BAD_REQUEST)
        product_stock.sale_mrp=mrp
        product_stock.discount=discount
        
        product_stock.save()
        serializers = ProductsStockListSerializer(product_stock)
        return Response(serializers.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def first_20_products(self, request, *args, **kwargs):
        product_stock = ProductsStock.objects.all().order_by("-inventory")[:20]
        serializers = ProductsStockListSerializer(product_stock, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)

    

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
            product_stock = ProductsStock.objects.get(id=id)
        except ProductsStock.DoesNotExist:
            return Response({"error":"product not present with given id"}, status=status.HTTP_400_BAD_REQUEST)
        serializers = ProductsStockListSerializer(product_stock)
        return Response(serializers.data, status=status.HTTP_200_OK)
       
    @action(detail=False, methods=['get'])
    def home_page(self, request, *args, **kwargs):
        res = {}
        queryset = ProductsStock.objects.all().select_related("product").order_by("-created_at")
        today_offer = queryset.filter(discount__gt=0)
        today_offer_serializer = ProductsStockListSerializer(today_offer , many=True)

        res["today_off"]=today_offer_serializer.data

        vegies = queryset.filter(product__category__name="vegitables")
        vegies_serializer = ProductsStockListSerializer(vegies , many=True)

        res["vegies"]=vegies_serializer.data

        green_vegies = queryset.filter(product__category__name="green_vegies")
        green_vegies_serializer = ProductsStockListSerializer(green_vegies , many=True)

        res["green_vegies"]=green_vegies_serializer.data


        salad = queryset.filter(product__category__name="salad")
        salad_serializer = ProductsStockListSerializer(salad , many=True)

        res["salad"]=salad_serializer.data

        return Response(res, status=status.HTTP_200_OK)