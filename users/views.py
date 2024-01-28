import re
from django.core.cache import cache
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from django.conf import settings
from django.dispatch import receiver
from django.contrib.auth.signals import user_logged_in
from rest_framework.decorators import action
from django.contrib.auth.hashers import check_password

from .filters import UserFilter
from .utils import generate_otp_and_key, send_custom_email, verify_otp
from .serializers import UserRoleSerializer, UserSerializer
import jwt
from .models import User
from datetime import datetime, timedelta
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import Group
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from duties.models import Routes
from django.db.models import Q
User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    model = User
    serializer_class = UserSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser)
    filter_backends = (DjangoFilterBackend,)
    filter_class = UserFilter
    permission_classes = (permissions.IsAuthenticated,)

    

    def get_queryset(self):
        queryset = User.objects.all().order_by('-created_at')
        return queryset

    def create(self, request, *args, **kwargs):
        return Response({},status=status.HTTP_405_METHOD_NOT_ALLOWED)


    @action(detail=False, methods=['post'],  permission_classes=[])
    def user_create(self, request, *args, **kwargs):
        user_data = request.data
        email = user_data.get('email', None)
        mb = user_data.get('phone_number', None)
        pincode = request.data.get('pincode', None)
        user_type = request.data.get('user_type', None)
        quadrant = request.data.get('quadrant', None)
        if not pincode:
            return Response({"error": "Pincode is required"},status=status.HTTP_400_BAD_REQUEST)
        if not user_type:
            return Response({"error": "user_type is required"},status=status.HTTP_400_BAD_REQUEST)
        
        user = User.objects.filter(Q(phone_number=mb) | Q(email=email))

        if user:
            return Response({"error": "user already exist with given email or mobile number"},status=status.HTTP_400_BAD_REQUEST)

        if user_type=="customer":
            try:
                user_q = Routes.objects.get(pincode=pincode)
            except Routes.DoesNotExist:
                return Response({"error": f"we are currently not serving in {pincode} pincode"},status=status.HTTP_400_BAD_REQUEST)
            user_data["quadrant"]=user_q.quadrant.id
        if user_type=="rider":
            if not quadrant:
                return Response({"error": "Quadrant  is required"},status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(data=user_data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        if not id:
            return Response({"error":"product id is missing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            route=User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error":"user does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = UserSerializer(route, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        updated_route=serializer.save()
        serializer=UserSerializer(updated_route)
        return Response(serializer.data, status=status.HTTP_200_OK)


    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
            route=User.objects.get(id=id)
        except User.DoesNotExist:
            return Response({"error":"user does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer=UserSerializer(route)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):  
        id = kwargs.get('pk')
        if not request.user.is_superuser:
            return Response({"error":"permission not allowed."}, status=status.HTTP_403_FORBIDDEN)
        try:
            user=User.objects.get(id=id).delete()
        except User.DoesNotExist:
            return Response({"error":"user does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)

        return Response({},status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['post'],  permission_classes=[])
    def login(self, request, *args, **kwargs):
        try:
            email = request.data['email']
            password = request.data['password']
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return Response({"error": f"Email id is not registered.", "stat": False}, status=status.HTTP_400_BAD_REQUEST)

            if not user.check_password(password):
                return Response({"message": "incorrect_credentials","stat": False}, status=status.HTTP_400_BAD_REQUEST)

            refresh = RefreshToken.for_user(user)

            user_details = {
                'id': user.id,
                'name': f"{user.first_name} {user.last_name}",
                'access_token': str(refresh.access_token),
                'stat': True,
	            'message': "Login successful",
                'user_type': user.user_type,
                'quadrant': user.quadrant.id if user.quadrant else None,
                'quadrant_name': user.quadrant.name if user.quadrant else None,
                'pincode': user.pincode
               
                
            }

            return Response(user_details, status=status.HTTP_200_OK)
        except KeyError:
            res = {'error': 'Please provide an email and a password'}
            return Response(res, status=status.HTTP_400_BAD_REQUEST)


    @action(detail=False, methods=['post'],  permission_classes=[])
    def forgot_password(self, request, *args, **kwargs):
        PASSWORD_RESET_KEY = "user_password_reset_key.{otp_key}"
        email = request.data['email']
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": f"user with {email} is not registered."}, status=status.HTTP_400_BAD_REQUEST)
        if user.otp:
                otp = str(otp)[:6]
        else:
            otp, otp_key = generate_otp_and_key(
                uuid=user.id, secret_key=PASSWORD_RESET_KEY)
            user.otp = otp
            user.save()
        send_custom_email("OTP from todo app.", f"Your One time Password is : {otp}", [user.email])
        return Response({"message": "OTP sent on registered email id."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[])
    def set_new_password(self, request, *args, **kwargs):
        email = request.data['email']
        password = request.data['password']
        otp = request.data['otp']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"error": f"user with {email} is not registered."}, status=status.HTTP_400_BAD_REQUEST)

        if user.otp:
            if otp !=user.otp:
                return Response({"error":"invalid otp."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"otp expired."}, status=status.HTTP_400_BAD_REQUEST)

        
        user.set_password(password)
        user.save(update_fields=["password"])
        user.otp=None
        user.save()
        return Response({"message":"Password changed succesfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], permission_classes=[])
    def otp_verification(self, request, *args, **kwargs):
        otp = request.data.get('otp', None)
        email = request.data['email']
        user = User.objects.get(email=email)
        if not otp:
            return Response({"error":"opt is required."}, status=status.HTTP_400_BAD_REQUEST)
        # response, otp_key = verify_otp(user_id=user.id, otp=otp)        
        if user.otp:
            if otp !=user.otp:
                return Response({"error":"invalid otp."}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"error":"otp expired."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"message":"OTP verified."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"])
    def create_roles(self, request, *args, **kwargs):
        if not request.user.is_superuser:
            return Response({"error":"permission not allowed."}, status=status.HTTP_403_FORBIDDEN)
        role_name= request.data.get("role_name")
        pattern = r"^[a-z_]+$"
        if not re.match(pattern, role_name):
            return Response({"error":"Role name should be in lowercase, does not contain spaces and should contains alphabetical characters and underscores."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            role = Group.objects.get(name=role_name)
            if role:
                return Response({"error":"Roles alerady exist with given name."}, status=status.HTTP_400_BAD_REQUEST)
        except:
            pass
        new_role = Group.objects.create(name=role_name)
        serializer = UserRoleSerializer(new_role)
        return Response(serializer.data, status=status.HTTP_200_OK)