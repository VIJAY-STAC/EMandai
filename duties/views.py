from datetime import datetime
import json
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from orders.models import B2COrders
from .models import *
from .serializers import * 
from datetime import datetime
from phonenumbers import format_number, PhoneNumberFormat
# Create your views here.

class RoutesViewSet(viewsets.ModelViewSet):
    model = Routes
    serializer_class = RoutesListSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Routes.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializers = RoutesSerializer(data=data)
        serializers.is_valid(raise_exception=True)
        route = serializers.save()
        serializer = RoutesListSerializer(route)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            route=Routes.objects.get(id=id)
        except Routes.DoesNotExist:
            return Response({"error":"route does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = RoutesSerializer(route, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_route=serializer.save()
        serializer=RoutesListSerializer(updated_route)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
           route=Routes.objects.get(id=id)
        except Routes.DoesNotExist:
            return Response({"error":"Product does not found with given id"},status=status.HTTP_400_BAD_REQUEST)
        serializer=RoutesListSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        routes=Routes.objects.all().order_by('-created_at')
        serializer=RoutesListSerializer(routes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def destroy(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED  )
        


class QuadrantsViewSet(viewsets.ModelViewSet):
    model = Quadrants
    serializer_class = QuadrantsSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Quadrants.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializers = QuadrantsSerializer(data=data)
        serializers.is_valid(raise_exception=True)
        route = serializers.save()
        serializer = QuadrantsSerializer(route)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            route=Quadrants.objects.get(id=id)
        except Quadrants.DoesNotExist:
            return Response({"error":"quadrant does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = QuadrantsSerializer(route, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_route=serializer.save()
        serializer=QuadrantsSerializer(updated_route)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
           route=Quadrants.objects.get(id=id)
        except Quadrants.DoesNotExist:
            return Response({"error":"quadrant does not found with given id"},status=status.HTTP_400_BAD_REQUEST)
        serializer=QuadrantsSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        quadrants=Quadrants.objects.all().order_by('-created_at')
        serializer=QuadrantsSerializer(quadrants, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def destroy(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 

class DutyViewSet(viewsets.ModelViewSet):
    model = Duty
    serializer_class = DutyListSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = Duty.objects.all()
        return queryset

    def create(self, request, *args, **kwargs):
        data = request.data
        serializers = DutySerializer(data=data)
        serializers.is_valid(raise_exception=True)
        route = serializers.save()
        serializer = DutyListSerializer(route)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            duty=Duty.objects.get(id=id)
        except Duty.DoesNotExist:
            return Response({"error":"quadrant does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DutySerializer(duty, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_duty=serializer.save()
        serializer=DutyListSerializer(updated_duty)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
           duty=Duty.objects.get(id=id)
        except Duty.DoesNotExist:
            return Response({"error":"duty does not found with given id"},status=status.HTTP_400_BAD_REQUEST)
        serializer=DutyListSerializer(duty)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def list(self, request, *args, **kwargs):
        duties=Duty.objects.all().order_by('-created_at')
        serializer=DutyListSerializer(duties, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK) 

    def destroy(self, request, *args, **kwargs):
        return Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED) 

    @action(detail=False, methods=['post'])
    def create_duty(self, request, *args, **kwargs):
        pending_orders = B2COrders.objects.filter(status="ready_to_delivery")
        if not pending_orders:
            return Response({"error":"order are not available"}, status=status.HTTP_400_BAD_REQUEST)
        quadrants_wise_orders = {}
        for order in pending_orders:
            if order.quadrant.name in quadrants_wise_orders:
                quadrants_wise_orders[order.quadrant.name].append(
                    order
                )
            else:
                quadrants_wise_orders[order.quadrant.name]=[order]

        for quadrants_wise_order in quadrants_wise_orders:
            current_time =  datetime.now()
            quad = quadrants_wise_orders[quadrants_wise_order][0].quadrant

            duty=Duty.objects.create(
                    name=quadrants_wise_order+" Duty "+" : "+str(current_time.strftime("%Y-%m-%d %H:%M:%S")),
                    quadrant=quad,
                    
            )
            orders = quadrants_wise_orders[quadrants_wise_order]
            oc=0
            for order in orders:
                order.duty=duty
                order.status = "out_for_delivery"
                order.customer_status="out_for_delivery"
                order.save(update_fields=["duty","status","customer_status"])
                oc +=1
            duty.total_outlets=oc
            duty.save(update_fields=["total_outlets"])
        return Response({"message":"duties created successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def duty_details(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({"error":"duty is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            duty = Duty.objects.get(id=id)
        except Duty.DoesNotExist:
            return Response({"error":"Duty does not exist with given id"}, status=status.HTTP_400_BAD_REQUEST)

        orders = B2COrders.objects.filter(duty_id=id)
        res = {}
        res["name"] = duty.name
        res["total_outlets"] = duty.total_outlets
        res["delivered_attempted_outlets"] = duty.delivered_attempted_outlets
        order_list = []
        for order in orders:
            data= {
                            "order_id": order.id,
                            "invoice_number": order.invoice_number,
                            "status": order.status,
                            "payment_type": order.payment_type,
                            "payment_status": order.payment_status,
                            "deliver_to":order.created_by.full_name,
                            "mobile":   format_number(order.created_by.phone_number, PhoneNumberFormat.E164),
                            "delivery_address": order.created_by.address,
                            "pincode": order.created_by.pincode,
                            "delivery_attempted": order.delivery_attempted


                        }
            order_list.append(data)
        res["orders"]=order_list
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def start_duty(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({"error":"duty is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            duty = Duty.objects.get(id=id)
        except Duty.DoesNotExist:
            return Response({"error":"Duty does not exist with given id"}, status=status.HTTP_400_BAD_REQUEST)

        if  duty.status!="assigned":
            return Response({"error":"duty status is not assigned"}, status=status.HTTP_400_BAD_REQUEST)
        duty.status="started"
        duty.started_at=datetime.now()
        duty.save(update_fields=["status","started_at"])
        return Response({"message":"Duty started successfully."}, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['post']) 
    def complete_duty(self, request, *args, **kwargs):
        id = request.data.get('id', None)
        if id is None:
            return Response({"error":"duty is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            duty = Duty.objects.get(id=id)
        except Duty.DoesNotExist:
            return Response({"error":"Duty does not exist with given id"}, status=status.HTTP_400_BAD_REQUEST)

        if duty.total_outlets!=duty.delivered_attempted_outlets:
            return Response({"error":f"{duty.total_outlets - duty.delivered_attempted_outlets} outlet pendings to delivered."},status=status.HTTP_400_BAD_REQUEST)
        if duty.status=="completed":
             return Response({"message":"Duty  already Completed."}, status=status.HTTP_400_BAD_REQUEST)
        duty.status="completed"
        duty.completed_at=datetime.now()
        duty.save(update_fields=["status","completed_at"])
        return Response({"message":"Duty Completed successfully."}, status=status.HTTP_200_OK)