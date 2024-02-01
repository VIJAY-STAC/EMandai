import uuid
from django.db import models
from phonenumber_field.modelfields import PhoneNumberField
from django.contrib.auth.models import AbstractUser
from django.urls import reverse

# Create your models here.

USER_Gender = (
    ('male','Male'),
    ('female','Female'),
)

USER_TYPES = (
    ('customer','Customer'),
    ('farmer','Farmer'),
    ('rider','Rider'),
    ('packer','Packer'),
    ('picker','Picker'),
    ('checker','Checker'),
    ('accountant','Accountant'),
    ('inward_manager','Inward Manager'),
    ('admin','Admin'),
)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    first_name = models.CharField(max_length=30, blank=False, null=False)
    last_name = models.CharField(max_length=30, blank=False, null=False)
    date_of_birth = models.DateField(null=True, blank=True)
    email = models.EmailField(max_length=40, unique=True)
    phone_number = PhoneNumberField(blank=True, null=True)
    address = models.CharField(max_length=500, null=False,blank=False)
    pincode = models.CharField(max_length=6, blank=False, null=False)
    latitude = models.CharField(max_length=15, blank=True, null=True)
    longitude = models.CharField(max_length=15, blank=True, null=True)
    gender = models.CharField(choices=USER_Gender,null=True, blank=True, max_length=20)
    otp = models.CharField(null=True, blank=True, max_length=6)
    user_type = models.CharField(
        null=False, blank=False, max_length=32, choices=USER_TYPES, 
    )
    quadrant = models.ForeignKey(   "duties.Quadrants", 
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name="user_quadrant"
                                )
    
    @property
    def full_name(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name, last_name=self.last_name
        )

    def __str__(self):
        return "{first_name} {last_name}".format(
            first_name=self.first_name, last_name=self.last_name
        )

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})