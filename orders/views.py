from datetime import datetime
import json
from rest_framework import parsers, status, permissions, viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from inventory.models import ProductsStock, FarmerProducts
from django.db.models import Sum
from .models import *
from .serializers import * 
# Create your views here.

class B2BOrdersViewSet(viewsets.ModelViewSet):
    model = B2BOrders
    serializer_class = B2BOrderListSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = B2BOrders.objects.all()
        return queryset

    def b2b_validation(self, skus):
        stock_not_available=[]
        for sku in skus:
            farmer_product = FarmerProducts.objects.get(id=sku['id'])
            if farmer_product.quantity<sku['qty']:
                stock_not_available.append(farmer_product.product.name)
        return stock_not_available


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            data= request.data
            skus = data.get('skus')
            stock_not_available=self.b2b_validation(skus)
            if stock_not_available:
                return Response({"error":"below products are out of stock.","skus":stock_not_available}, status=status.HTTP_400_BAD_REQUEST)
            serializers = B2BOrderSerializer(data=data)
            serializers.is_valid(raise_exception=True)
            order = serializers.save(created_by=request.user)
            b2b_products = []
            total_amount = 0
            
            for sku in skus:
                farmer_product = FarmerProducts.objects.get(id=sku['id'])
                ta= farmer_product.mrp*sku['qty'] # ta = total amount of sku
                total_amount += ta
            
                b2b_products.append(
                    OrderProducts(
                        b2bproduct_id=farmer_product.product_id,
                        b2border_id=order.id,
                        quantity=sku['qty'],
                        amt=farmer_product.mrp,
                        total_amt=ta,
                        farmer_product_id=farmer_product.id
                    )
                )
            OrderProducts.objects.bulk_create(b2b_products)
            order.amount=total_amount
            order.i_v=total_amount
            order.save()
            serializer = B2BOrderListSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

            

    @action(detail=False, methods=['post'])
    def accept_b2b_order(self, request, *args, **kwargs):
        id = request.data.get('id',None)
        if not id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2BOrders.objects.get(id=id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)

        order.status= "accepted"
        order.save()
        return Response("Order accepted.", status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def checking_b2b_products(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        op_id = request.data.get('op_id',None) # op_id= order product id
        qty = request.data.get('qty',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2BOrders.objects.get(id=o_id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)

        if order.status!= "accepted":
            return Response({"error":"order not accepted yet."}, status=status.HTTP_400_BAD_REQUEST)

        products = OrderProducts.objects.get(id=op_id,b2border=order)
        updated_qty = products.checked_qty + qty
        if updated_qty>products.quantity:
            return Response({"error":f"{updated_qty-products.quantity} quantity extra detected."}, status=status.HTTP_400_BAD_REQUEST)

        products.checked_qty =  updated_qty
        products.total_amt= updated_qty * products.amt
        products.save(update_fields=["checked_qty","total_amt"])

        farmer_products = FarmerProducts.objects.get(id=products.farmer_product.id)
        farmer_products.quantity -= qty
        farmer_products.save(update_fields=["quantity"])

        return Response({"message":f"{qty} quantity of {products.b2bproduct.name} recieved successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def b2b_checking_done(self, request, *args, **kwargs):   
        o_id = request.data.get('o_id',None)
        enforce = request.data.get('enforce',False)
        
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2BOrders.objects.get(id=o_id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        if enforce==False:
            products = OrderProducts.objects.filter(b2border=order)
            mismatch = []
            for product in products:
                if product.quantity!=product.checked_qty:
                    mismatch.append(
                        {
                            "product": product.b2bproduct.name,
                            "quantity": product.quantity,
                            "checked_qty": product.checked_qty if product.checked_qty else None,
                        }
                    )
            if mismatch:
                return Response({"error":mismatch}, status=status.HTTP_400_BAD_REQUEST)

        return Response({"message":"Order checked successfully"}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def b2b_order_invoice(self, request, *args, **kwargs):
        o_id = request.query_params.get('o_id',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2BOrders.objects.get(id=o_id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 

        skus= OrderProducts.objects.filter(b2border=o_id)
        sku_data = []
        order_amount = 0.0
        for sku in skus:
            order_amount +=float(sku.total_amt)
            data= {
                "id": sku.id,
                "product": sku.b2bproduct.name,
                "quantity": sku.quantity,
                "amount": sku.amt,
                "totalAmount": sku.total_amt,
                "checked_qty": sku.checked_qty,
                
            }
            sku_data.append(data)

        result = {
            "order": order.id,
            "status":order.status,
            "amount": order_amount,
            "payment_status": order.payment_status,
            "payment_type":order.payment_type,
            "skus": sku_data
        }
        order.amount=order_amount
        order.save(update_fields=["amount"])
        order.save()
        return Response(result, status=status.HTTP_200_OK)



    @action(detail=False, methods=['get'])
    def b2b_order_details(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        order = B2BOrders.objects.get(id=id)
        skus= OrderProducts.objects.filter(b2border=id)
        sku_data = []
        for sku in skus:
            data= {
                "id": sku.id,
                "product": sku.b2bproduct.name,
                "quantity": sku.quantity,
                "amount": sku.amt,
                "totalAmount": sku.total_amt,
                "checked_qty": sku.checked_qty,
                
            }
            sku_data.append(data)

        result = {
            "order": order.id,
            "status":order.status,
            "amount": order.amount,
            "payment_status": order.payment_status,
            "payment_type":order.payment_type,
            "skus": sku_data
        }
        return Response(result, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['post'])
    def b2b_order_payment(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        p_amt =request.data.get('p_amt',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2BOrders.objects.get(id=o_id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 
        
        if p_amt>(order.amount-order.collected_amount):
            return Response({"error":f"You are paying Rs {p_amt-(order.amount-order.collected_amount)} extra."}, status=status.HTTP_400_BAD_REQUEST) 
        elif p_amt<order.amount:
            return Response({"error":f"You are paying Rs {(order.amount-order.collected_amount)-p_amt} less."}, status=status.HTTP_400_BAD_REQUEST) 

        order.collected_amount = p_amt
        order.status ="delivered"
        order.payment_status="paid"
        order.save(update_fields=["collected_amount","status","payment_status"])
        return Response({"message":"Payment recived successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def b2b_order_products_inward(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2BOrders.objects.get(id=o_id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 

        if order.is_inward_done==True:
            return Response({"error":"order stock already inwarded."}, status=status.HTTP_400_BAD_REQUEST)             

        skus= OrderProducts.objects.filter(b2border=order)
        e_p = {}
        existing_products = ProductsStock.objects.all() # existing_products
        for pro in existing_products:
            e_p[pro.product.id]=pro

        for sku in skus:
            if sku.b2bproduct.id in e_p:
                update_product_stock = ProductsStock.objects.get(product_id=sku.b2bproduct.id)
                update_product_stock.inventory += sku.checked_qty
                update_product_stock.save(update_fields=["inventory"])
            else:
              
                ProductsStock.objects.create(
                product=sku.b2bproduct,
                expiry_date=sku.expiry_date,
                inventory=sku.quantity,
                available=True,
                sale_mrp=sku.amt+10
                )

            
        order.is_inward_done = True
        order.save(update_fields=["is_inward_done"])
        
        return Response({"message": "Products stock updated successfully"},status=status.HTTP_200_OK)

class B2COrdersViewSet(viewsets.ModelViewSet):
    model = B2COrders
    serializer_class = B2COrderSerializer
    parser_classes = (parsers.FormParser, parsers.JSONParser, parsers.MultiPartParser)
    filter_backends = (DjangoFilterBackend,)
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = B2COrders.objects.all().order_by('-created_at')
        return queryset

    def b2c_validation(self, skus):
        stock_not_available=[]
        for sku in skus:
            prod = ProductsStock.objects.get(id=sku['id'])
            if prod.inventory<sku['qty']:
                stock_not_available.append({"p_name":prod.product.name,"available":prod.inventory})
        return stock_not_available


    def create(self, request, *args, **kwargs):
        with transaction.atomic():
            data= request.data
            skus = data.get('skus')
            stock_not_available=self.b2c_validation(skus)
            if stock_not_available:
                return Response({"error":"below products are out of stock.","skus":stock_not_available}, status=status.HTTP_400_BAD_REQUEST)
            data["quadrant"]=request.user.quadrant.id
            serializers = B2COrderSerializer(data=data)
            serializers.is_valid(raise_exception=True)
            order = serializers.save(created_by=request.user)
            b2c_products = []
            stock_not_available=[]
            total_amount = 0.00
            for sku in skus:
                    prod = ProductsStock.objects.get(id=sku['id'])
                    ta = prod.sale_mrp*sku['qty'] # ta = total amount of sku
                    total_amount = total_amount + float(ta)
                    b2c_products.append(
                        OrderProducts(
                            b2cproduct_id=sku['id'],
                            b2corder=order,
                            quantity=sku['qty'],
                            amt=prod.sale_mrp,
                            total_amt=ta,
                            product_stock=prod
                        )
                    )
                    prod.inventory -= sku['qty']
                    prod.save(update_fields=["inventory"])
            OrderProducts.objects.bulk_create(b2c_products)
            order.amount=total_amount
            order.i_v=total_amount
            order.save()
            serializer = B2COrderSerializer(order)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        try:
            order = B2COrders.objects.get(id=id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
        serializer=B2COrderRetrivewSerializer(order)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def accept_b2c_order(self, request, *args, **kwargs):
        id = request.data.get('id',None)
        if not id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)

        order.status= "accepted"
        order.customer_status = "accepted"
        order.save()
        return Response("Order accepted.", status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def checking_b2c_products(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        op_id = request.data.get('op_id',None) # op_id= order product id
        qty = request.data.get('qty',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)

        if order.status!= "accepted":
            return Response({"error":"order not accepted yet."}, status=status.HTTP_400_BAD_REQUEST)

        products = OrderProducts.objects.get(id=op_id,b2corder=order)
        updated_qty = products.checked_qty + qty
        if updated_qty>products.quantity:
            return Response({"error":f"{updated_qty-products.quantity} quantity extra detected."}, status=status.HTTP_400_BAD_REQUEST)

        products.checked_qty =  updated_qty
        products.total_amt= updated_qty * products.amt
        products.save(update_fields=["checked_qty","total_amt"])
        return Response({"message":f"{qty} quantity of {products.b2cproduct.product.name} recieved successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def b2c_checking_done(self, request, *args, **kwargs):   
        o_id = request.data.get('o_id',None)
     
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2BOrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST)
    
        products = OrderProducts.objects.filter(b2corder=order)
        mismatch = []
        for product in products:
            if product.quantity!=product.checked_qty:
                mismatch.append(
                    {
                        "product": product.b2cproduct.product.name,
                        "quantity": product.quantity,
                        "checked_qty": product.checked_qty if product.checked_qty else None,
                    } 
                )
        if mismatch:
            return Response({"error":mismatch}, status=status.HTTP_400_BAD_REQUEST)
        order.status="ready_to_delivery"
        order.customer_status="ready_to_delivery"
        order.save(update_fields=["status","customer_status"])
        return Response({"message":"Order is ready for delivery"}, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['get'])
    def b2c_order_invoice(self, request, *args, **kwargs):
        o_id = request.query_params.get('o_id',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 

        skus= OrderProducts.objects.filter(b2corder=o_id)
        sku_data = []
        order_amount = 0.0
        for sku in skus:
            order_amount +=float(sku.total_amt)
            data= {
                "id": sku.id,
                "product": sku.b2cproduct.product.name,
                "quantity": sku.quantity,
                "amount": sku.amt,
                "totalAmount": sku.total_amt,
                "checked_qty": sku.checked_qty,
                
            }
            sku_data.append(data)

        result = {
            "order": order.id,
            "status":order.status,
            "amount": order_amount,
            "payment_status": order.payment_status,
            "payment_type":order.payment_type,
            "skus": sku_data
        }
        order.amount=order_amount
        order.save(update_fields=["amount"])
        order.save()
        return Response(result, status=status.HTTP_200_OK)



    @action(detail=False, methods=['get'])
    def b2c_order_details(self, request, *args, **kwargs):
        id = request.query_params.get("id")
        order = B2COrders.objects.get(id=id)
        skus= OrderProducts.objects.filter(b2corder=id)
        sku_data = []
        for sku in skus:
            data= {
                "id": sku.id,
                "product": sku.b2cproduct.product.name,
                "quantity": sku.quantity,
                "amount": sku.amt,
                "totalAmount": sku.total_amt,
                "checked_qty": sku.checked_qty,
                
            }
            sku_data.append(data)

        result = {
            "order": order.id,
            "user": order.created_by.full_name,
            "quandrant": order.quadrant.name,
            "status":order.status,
            "amount": order.amount,
            "payment_status": order.payment_status,
            "payment_type":order.payment_type,
            "skus": sku_data
        }
        return Response(result, status=status.HTTP_200_OK)

    
    @action(detail=False, methods=['post'])
    def delivered_b2c_order(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 
        op_update=[]
        if order.status!="out_for_delivery":
            return Response({"error":"order status is not out_for_delivery."}, status=status.HTTP_400_BAD_REQUEST) 
        if order.payment_status!="paid":
            return Response({"error":"Payment is pending."}, status=status.HTTP_400_BAD_REQUEST) 
        skus= OrderProducts.objects.filter(b2corder=order.id)
        for sku in skus:
                sku.delivered_qty=sku.quantity
                op_update.append(sku)
        OrderProducts.objects.bulk_update(op_update,["delivered_qty"]) 
        order.status ="delivered"
        order.customer_status="delivered"
        order.delivery_attempted=True
        order.save(update_fields=["status","delivery_attempted","customer_status"])
        duty=Duty.objects.get(id=order.duty.id)
        duty.delivered_attempted_outlets += 1
        duty.save(update_fields=["delivered_attempted_outlets"])
        return Response({"message":"Order delivered successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def b2c_order_payment(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        p_amt =request.data.get('p_amt',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 
        
        if p_amt>(order.amount-order.collected_amount):
            return Response({"error":f"You are paying Rs {p_amt-(order.amount-order.collected_amount)} extra."}, status=status.HTTP_400_BAD_REQUEST) 
        elif p_amt<order.amount:
            return Response({"error":f"You are paying Rs {(order.amount-order.collected_amount)-p_amt} less."}, status=status.HTTP_400_BAD_REQUEST) 

        order.collected_amount = p_amt
        order.payment_status="paid"
        order.save(update_fields=["collected_amount","payment_status"])
        return Response({"message":"Payment recived successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def cancel_b2c_order(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        notes=request.data.get('notes',None)
        if not notes:
            return Response({"error":"notes is required"}, status=status.HTTP_400_BAD_REQUEST)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 
        if order.status in ["cancelled","r_a_wh"]:
            return Response({"error":"order is already cancelled."}, status=status.HTTP_400_BAD_REQUEST) 
        op_update=[]
        prod_stock_update=[]
        total_amount = 0
        if order.status in ["placed","accepted"]:
            skus= OrderProducts.objects.filter(b2corder=order.id)
            for sku in skus:
                    prod = ProductsStock.objects.get(id=sku.b2cproduct.id)
                    ta = sku.amt*sku.quantity # ta = total amount of sku
                    total_amount = total_amount + ta

                    sku.return_qty=sku.quantity
                    sku.total_amt=sku.total_amt-ta
                    op_update.append(sku)
                    
                    prod.inventory += sku.quantity
                    prod_stock_update.append(prod)
            OrderProducts.objects.bulk_update(op_update,["return_qty","total_amt"]) 
            ProductsStock.objects.bulk_update(prod_stock_update,["inventory"]) 
            order.amount=order.amount-total_amount
            order.status ="r_a_wh"
            order.customer_status="cancelled"
            order.notes=notes
            order.save(update_fields=["status","amount","notes","customer_status"])
        elif  order.status in ["ready_to_delivery","out_for_delivery","delivered"]:
            order.status ="cancelled"
            order.notes=notes
            order.save(update_fields=["status","notes"])
        return Response({"message":"Order cancelled successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def returned_b2c_order(self, request, *args, **kwargs):
        o_id = request.data.get('o_id',None)
        if not o_id:
            return Response({"error":"order id is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = B2COrders.objects.get(id=o_id)
        except B2COrders.DoesNotExist:
            return Response({"error":"order does not exist with given id."}, status=status.HTTP_400_BAD_REQUEST) 
        if order.status !="cancelled":
            return Response({"error":"order status is not cancelled."}, status=status.HTTP_400_BAD_REQUEST) 
       
        op_update=[]
        prod_stock_update=[]
        total_amount = 0
        skus= OrderProducts.objects.filter(b2corder=order.id)
        for sku in skus:
                prod = ProductsStock.objects.get(id=sku.b2cproduct.id)
                ta = sku.amt*sku.quantity # ta = total amount of sku
                total_amount = total_amount + ta

                sku.return_qty=sku.quantity
                sku.total_amt=sku.total_amt-ta
                op_update.append(sku)
                
                prod.inventory += sku.quantity
                prod_stock_update.append(prod)
        OrderProducts.objects.bulk_update(op_update,["return_qty","total_amt"]) 
        ProductsStock.objects.bulk_update(prod_stock_update,["inventory"]) 
        order.amount=order.amount-total_amount
        order.status ="r_a_wh"
        order.save(update_fields=["status","amount"])
        return Response({"message":"Order cancelled successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def add_to_cart(self, request, *args, **kwargs):
        product_id = request.data.get('product_id',None)
        qty = request.data.get('qty',None)
        if not product_id:
            return Response({"error":"Product id is required."},status=status.HTTP_400_BAD_REQUEST)
        if not qty:
            return Response({"error":"quantity is required."},status=status.HTTP_400_BAD_REQUEST)
        try:
            product = ProductsStock.objects.get(id=product_id)
        except ProductsStock.DoesNotExist:
            return Response({"error":"product does not exist with given id."},status=status.HTTP_400_BAD_REQUEST)
        
        if product.inventory<qty:
            return Response({"error":f"Current stock is {product.inventory}."},status=status.HTTP_400_BAD_REQUEST)
        try:
            cart = Cart.objects.get(product=product_id, user=request.user)
        except Cart.DoesNotExist:
            cart=None

        if cart:
            cart.quantity=qty
            cart.amt=product.sale_mrp
            cart.total_amt= product.sale_mrp*qty
            cart.save(update_fields=["quantity","amt","total_amt"])
        else:
            Cart.objects.create(
                product=product,
                quantity=qty,
                amt=product.sale_mrp,
                total_amt= product.sale_mrp*qty,
                user=request.user
            )
        return Response({"message":"product added in cart successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def cart_list(self, request, *args, **kwargs):
        cart_list = Cart.objects.filter(user=request.user)
        serializers = CartSerializer(cart_list, many=True)

        total = cart_list.aggregate(total=Sum("total_amt"))
        res = {
            "cart_list":serializers.data,
            "total":total["total"]

        }
        return Response(res, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def cart_items_count(self, request, *args, **kwargs):
        cart_list = Cart.objects.filter(user=request.user)
        return Response(len(cart_list), status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def update_cart(self, request, *args, **kwargs):
        cart_id = request.data.get('cart_id',None)
        qty = request.data.get('qty',None)
        if not cart_id:
            return Response({"error":"Product id is required."},status=status.HTTP_400_BAD_REQUEST)
        if qty==None:
            return Response({"error":"quantity is required."},status=status.HTTP_400_BAD_REQUEST)
        try:
            cart = Cart.objects.get(id=cart_id)
        except Cart.DoesNotExist:
            return Response({"error":"Cart does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product = ProductsStock.objects.get(id=cart.product.id)
        except ProductsStock.DoesNotExist:
            return Response({"error":"product does not exist with given id."},status=status.HTTP_400_BAD_REQUEST)
        
        if product.inventory<qty:
            return Response({"error":f"Current stock is {product.inventory}."},status=status.HTTP_400_BAD_REQUEST)
        if qty==0:
            cart.delete()
        elif qty>0:
            cart.quantity=qty
            cart.amt=product.sale_mrp
            cart.total_amt= product.sale_mrp*qty
            cart.save(update_fields=["quantity","amt","total_amt"])
        return Response({"message":"Cart updated successfully."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'])
    def cart_to_order(self, request, *args, **kwargs):
        with transaction.atomic():
            payment_type=request.data.get('payment_type',None)
            payment_status=request.data.get('payment_status',None)
            if not payment_type:
                return Response({"error":"payment type is required."}, status=status.HTTP_400_BAD_REQUEST)
            products =[]
            data={
                "order_type":"b2c",
                "status":"placed",
                "amount":0,
                "payment_type":payment_type,
                "payment_status":payment_status,
            }
            carts = Cart.objects.filter(user=request.user)
            if not carts:
                return Response({"message":"Cart is empty."}, status=status.HTTP_200_OK)
            for cart in carts:
                product = ProductsStock.objects.get(id=cart.product.id)
                qty = cart.quantity
                products.append({"id":product.id,"qty":qty})
            
            skus = products
            stock_not_available=self.b2c_validation(skus)
            if stock_not_available:
                return Response({"error":"below products are out of stock.","skus":stock_not_available}, status=status.HTTP_400_BAD_REQUEST)
            data["quadrant"]=request.user.quadrant.id
            serializers = B2COrderSerializer(data=data)
            serializers.is_valid(raise_exception=True)
            order = serializers.save(created_by=request.user)
            b2c_products = []
            stock_not_available=[]
            total_amount = 0.00
            for sku in skus:
                    prod = ProductsStock.objects.get(id=sku['id'])
                    ta = prod.sale_mrp*sku['qty'] # ta = total amount of sku
                    total_amount = total_amount + float(ta)
                    b2c_products.append(
                        OrderProducts(
                            b2cproduct_id=sku['id'],
                            b2corder=order,
                            quantity=sku['qty'],
                            amt=prod.sale_mrp,
                            total_amt=ta,
                            product_stock=prod
                        )
                    )
                    prod.inventory -= sku['qty']
                    prod.save(update_fields=["inventory"])
            OrderProducts.objects.bulk_create(b2c_products)
            order.amount=total_amount
            order.i_v=total_amount
            order.save()
            serializer = B2COrderSerializer(order)
            carts.delete()
            return Response(serializer.data, status=status.HTTP_200_OK)

        
    @action(detail=False, methods=['get'])
    def customer_order_list(self, request, *args, **kwargs):
        invoice_num = request.query_params.get('invoice_number',None)
        orders =B2COrders.objects.filter(created_by=request.user).order_by('-created_at')
        if invoice_num is not None:
            orders =orders.filter(invoice_number__icontains=invoice_num)
        serializers = B2COrderSerializer(orders, many=True)
        return Response(serializers.data, status=status.HTTP_200_OK)