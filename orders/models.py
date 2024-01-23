import uuid
from django.db import models
from duties.models import Duty
from users.models import User

from inventory.models_core import PrimaryUUIDTimeStampedModel, CreatedByModel, LastModifiedByModel

# Create your models here.
Order_type = (
    ('b2b','B2B'),
    ('b2c','B2C'),
)

Order_status=(
    ('placed','Placed'),
    ('accepted','Accepted'),
    ('ready_to_delivery','Ready to Delivery'),
    ('out_for_delivery','Out for delivery'),
    ('delivered','Delivered'),
    ('cancelled','Cancelled'),
    ('r_a_wh','Received at Warehouse')
)
Payment_type=(
    ('online','Online'),
    ('cash','Cash')
)

Payment_status=(
    ('paid','Paid'),
    ('unpaid','Unpaid'),
    ('refunded','Refunded'),
    ('na','NA')
)

class B2BOrders(CreatedByModel, LastModifiedByModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=20,null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    order_type= models.CharField(max_length=10, blank=False, null=False, choices=Order_type)
    initial_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2 , default=0.0)
    status= models.CharField(max_length=20, blank=False, null=False, choices=Order_status)
    payment_status= models.CharField(max_length=20, blank=False, null=False, choices=Payment_status,default="unpaid")
    payment_type = models.CharField(max_length=20, blank=False, null=False, choices=Payment_type)
    order_to= models.ForeignKey(
                                User,
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="b2b_far_user"
                            )
    is_inward_done = models.BooleanField(default=False)


    def save(self, *args, **kwargs):
        if not self.invoice_number:  # Only generate if the field is not set
            last_invoice_number = B2BOrders.objects.order_by('-created_at').values_list('invoice_number', flat=True).first()

            if last_invoice_number:
                prefix, last_number = last_invoice_number.split('-')
                new_number = int(last_number) + 1
            else:
                # If no existing invoice number, start from 1
                new_number = 1

            self.invoice_number = f'B2B-{new_number}'

        super(B2BOrders, self).save(*args, **kwargs)
    def __str__(self) :
        return self.invoice_number
            
class B2COrders(CreatedByModel, LastModifiedByModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    invoice_number = models.CharField(max_length=20,null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    order_type= models.CharField(max_length=10, blank=False, null=False, choices=Order_type)
    i_v = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    collected_amount = models.DecimalField(max_digits=10, decimal_places=2 , default=0.0)
    status= models.CharField(max_length=20, blank=False, null=False, choices=Order_status)
    payment_type = models.CharField(max_length=10, blank=False, null=False, choices=Payment_type)
    payment_status= models.CharField(max_length=20, blank=False, null=False, choices=Payment_status)
    duty = models.ForeignKey(Duty, null=True,blank=True,on_delete=models.SET_NULL,related_name="duty_order")
    quadrant = models.ForeignKey(   "duties.Quadrants", 
                                    null=True,
                                    blank=True,
                                    on_delete=models.SET_NULL,
                                    related_name="order_quadrant"
                                )
    delivery_attempted = models.BooleanField(default=False)
    notes = models.CharField(max_length=200, blank=True, null=True)
    def save(self, *args, **kwargs):
        if not self.invoice_number:  # Only generate if the field is not set
            last_invoice_number = B2COrders.objects.order_by('-created_at').values_list('invoice_number', flat=True).first()

            if last_invoice_number:
                prefix, last_number = last_invoice_number.split('-')
                new_number = int(last_number) + 1
            else:
                # If no existing invoice number, start from 1
                new_number = 1

            self.invoice_number = f'E-{new_number}'

        super(B2COrders, self).save(*args, **kwargs)
    def __str__(self) :
        return self.invoice_number

class OrderProducts(CreatedByModel):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    b2bproduct = models.ForeignKey(
                                "inventory.Products",
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="b2b_product"
                                )
    b2cproduct = models.ForeignKey(
                                "inventory.ProductsStock",
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="b2c_product"
                                )
    b2border = models.ForeignKey(
                                B2BOrders,
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE,
                                related_name="b2b_order"
                                )
    b2corder = models.ForeignKey(
                                B2COrders,
                                null=True,
                                blank=True,
                                on_delete=models.CASCADE,
                                related_name="b2c_order"
                                )
    farmer_product =  models.ForeignKey(
                                "inventory.FarmerProducts",
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="farmer_product"
                                )
    product_stock =  models.ForeignKey(
                                "inventory.ProductsStock",
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="product_stock"
                                )
    
    quantity = models.IntegerField(blank=False,null=False,default=0)
    discount = models.IntegerField(blank=False,null=False,default=0)
    checked_qty = models.IntegerField(blank=False,null=False,default=0)
    delivered_qty = models.IntegerField(blank=False,null=False,default=0)
    return_qty = models.IntegerField(blank=False,null=False,default=0)
    amt = models.DecimalField(blank=False,null=False,default=0, max_digits=6,decimal_places=2)
    expiry_date = models.DateField(null=True, blank=True,)
    total_amt =  models.DecimalField(blank=False,null=False,default=0, max_digits=6,decimal_places=2)

class Cart(models.Model):
    id = models.UUIDField(primary_key=True,default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    product = models.ForeignKey(
                                "inventory.ProductsStock",
                                null=True,
                                blank=True,
                                on_delete=models.SET_NULL,
                                related_name="cart_product"
                                )
    quantity = models.IntegerField(null=False,blank=False,default=0)
    amt = models.DecimalField(max_digits=5,decimal_places=2,default=0)
    total_amt =  models.DecimalField(blank=False,null=False,default=0, max_digits=6,decimal_places=2)
    user = models.ForeignKey(
                        User,
                        null=True,
                        blank=True,
                        on_delete=models.CASCADE,
                        related_name="user_cart")