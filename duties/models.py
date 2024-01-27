import uuid
from django.db import models

from users.models import User
# Create your models here.

Duty_status=(
    ("assigned", "Assigned"),
    ("started", "Started"),
    ("completed", "Completed"),
)

Duty_stop_status=(
    ("not_available", "Not Available"),
    ("completed", "Completed"),
    ("rescheduled", "Rescheduled"),
)


class Quadrants(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = [("name" )  ]
    def __str__(self):
        return self.name


class Routes(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    pincode = models.CharField(max_length=6, blank=False, null=False,unique=True)
    areas = models.CharField(max_length=50, blank=True, null=True)
    quadrant = models.ForeignKey(   Quadrants, 
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name="route_quadrant"
                                )
    is_active = models.BooleanField(default=False)

    class Meta:
        unique_together = [("pincode","quadrant")  ]

    def __str__(self):
        return self.name

class Duty(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    name = models.CharField(max_length=50, blank=False, null=False)
    started_at = models.DateTimeField( blank=True,null=True)
    completed_at = models.DateTimeField( blank=True,null=True)
    status = models.CharField(max_length=10, choices=Duty_status, blank=False,  default="assiged")
    total_outlets = models.IntegerField(blank=False, null=False, default=0)
    delivered_attempted_outlets = models.IntegerField(blank=False, null=False, default=0)
    quadrant = models.ForeignKey(   Quadrants, 
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name="duty_quadrant"
                                )
    rider = models.ForeignKey(
                    User,
                    blank=True,
                    null=True,
                    on_delete=models.SET_NULL,
                    related_name="duty_rider"

    )

    def __str__(self):
        return str(self.id)

