from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *



router = DefaultRouter()
router.register(r"products",ProductsViewSet,basename="products")
router.register(r"category",CategoryViewSet,basename="category")
router.register(r"farmer_product",FarmerProductsViewSet,basename="farmer_product")
router.register(r"product_stock",ProductsStockViewSet,basename="product_stock")
urlpatterns = [
    path('api/v1/',include(router.urls))
]