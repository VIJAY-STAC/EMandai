# Generated by Django 4.0.2 on 2024-01-14 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('inventory', '0006_alter_farmerproducts_packaging_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='productsstock',
            name='discount',
            field=models.IntegerField(blank=True, default=0, null=True),
        ),
    ]
