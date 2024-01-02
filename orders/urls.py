from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"b2b",B2BOrdersViewSet,basename="b2b")
router.register(r"b2c",B2COrdersViewSet,basename="b2c")
urlpatterns = [
    path('api/v1/',include(router.urls))
]