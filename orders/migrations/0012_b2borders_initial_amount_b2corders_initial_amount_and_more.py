# Generated by Django 4.0.2 on 2023-12-31 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0011_orderproducts_product_stock'),
    ]

    operations = [
        migrations.AddField(
            model_name='b2borders',
            name='initial_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='b2corders',
            name='initial_amount',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AlterField(
            model_name='b2borders',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('refunded', 'Refunded'), ('na', 'NA')], default='unpaid', max_length=20),
        ),
        migrations.AlterField(
            model_name='b2borders',
            name='status',
            field=models.CharField(choices=[('placed', 'Placed'), ('accepted', 'Accepted'), ('ready_to_delivery', 'Ready to Delivery'), ('out_for_delivery', 'Out for delivery'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('r_a_wh', 'Received at Warehouse')], max_length=20),
        ),
        migrations.AlterField(
            model_name='b2corders',
            name='payment_status',
            field=models.CharField(choices=[('paid', 'Paid'), ('unpaid', 'Unpaid'), ('refunded', 'Refunded'), ('na', 'NA')], max_length=20),
        ),
        migrations.AlterField(
            model_name='b2corders',
            name='status',
            field=models.CharField(choices=[('placed', 'Placed'), ('accepted', 'Accepted'), ('ready_to_delivery', 'Ready to Delivery'), ('out_for_delivery', 'Out for delivery'), ('delivered', 'Delivered'), ('cancelled', 'Cancelled'), ('r_a_wh', 'Received at Warehouse')], max_length=20),
        ),
    ]
