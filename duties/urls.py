from django.urls import path,include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r"routes",RoutesViewSet,basename="routes")
router.register(r"quadrants",QuadrantsViewSet,basename="quadrants")
router.register(r"duty",DutyViewSet,basename="duty")
urlpatterns = [
    path('api/v1/',include(router.urls))
]