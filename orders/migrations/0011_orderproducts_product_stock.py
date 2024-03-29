# Generated by Django 4.0.2 on 2023-12-28 19:43

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0005_alter_farmerproducts_mrp_and_more'),
        ('orders', '0010_alter_orderproducts_farmer_product'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderproducts',
            name='product_stock',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='product_stock', to='inventory.productsstock'),
        ),
    ]
