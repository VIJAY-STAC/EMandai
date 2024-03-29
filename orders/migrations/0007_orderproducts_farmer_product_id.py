# Generated by Django 4.0.2 on 2023-12-28 18:38

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0004_alter_productsstock_expiry_date'),
        ('orders', '0006_b2borders_is_inward_done_orderproducts_expiry_date'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproducts',
            name='farmer_product_id',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='farmer_product', to='inventory.farmerproducts'),
        ),
    ]
