from django.db import models
from django.conf import settings
from orders.models import B2COrders, B2BOrders,OrderProducts
from users.models import User
from .models_core import *
# Create your models here.


Payment_methods=(
    ('cash','Cash'),
    ('upi','upi'),
    ('credit','Credit'),
    ('cheque','cheque'),
)

Category_types=(
    ('green_vegies','Green Vegies'),
    ('vegitables','Vegetables'),
)

Packaging_types = (
    ('kg',"KG"),
)

class File(PrimaryUUIDTimeStampedModel):
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, on_delete=models.SET_NULL
    )
    name = models.CharField(max_length=120, null=False, blank=False)
    key = models.CharField(max_length=300, null=True, blank=True)
    url = models.URLField(blank=False, null=False)
    size = models.PositiveIntegerField(default=0)
    file_type = models.CharField(max_length=120, null=False, blank=False)

    def __str__(self):
        return self.url
    

class Category(PrimaryUUIDTimeStampedModel):
    name = models.CharField(max_length=60,choices=Category_types, blank=False, null=False)

class Products(PrimaryUUIDTimeStampedModel, CreatedByModel, LastModifiedByModel):
    name = models.CharField(max_length=60, blank=False, null=False)
    category = models.ForeignKey(
                                Category,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="p_category"
                            )
    product_images = models.ManyToManyField(
        File,
        related_name="product_images"
    )
    description = models.CharField(max_length=100, blank=True, null=True)
    packaging = models.CharField(max_length=20, blank=True, null=True, choices=Packaging_types) 
    
    def __str__(self):
        return self.name



class ProductsStock(PrimaryUUIDTimeStampedModel, CreatedByModel, LastModifiedByModel):
    product = models.ForeignKey(
                                Products,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="product_stock"
                                )
    sale_mrp = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    expiry_date = models.DateField(null=True, blank=True,)
    inventory = models.IntegerField(null=False, blank=False, default=0)
    available = models.BooleanField(null=False, blank=False, default=True)
    discount = models.IntegerField(default=0, null=True, blank=True)


    class Meta:
        unique_together = [(
            "product",
            "sale_mrp",
            "expiry_date")
        ]
    def __str__(self) :
        return self.product.name

class FarmerProducts(PrimaryUUIDTimeStampedModel, CreatedByModel, LastModifiedByModel):
    product = models.ForeignKey(
                                Products,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="farmer_product"
                                )
    mrp = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    expiry_date = models.DateField(null=False, blank=False)
    packaging = models.CharField(max_length=20, blank=False, null=False, choices=Packaging_types)   
    quantity = models.IntegerField(null=False, blank=False, default=0)
    farmer = models.ForeignKey(
                                User,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="farmer_user"
                            )

    class Meta:
        unique_together = [
            ("product", "mrp", "expiry_date", "packaging", "farmer")
        ]

    def __str__(self) :
        return self.product.name