# Generated by Django 4.0.2 on 2024-01-14 08:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_quadrant'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('customer', 'Customer'), ('farmer', 'Farmer'), ('rider', 'Rider'), ('packer', 'Packer'), ('picker', 'Picker'), ('checker', 'Checker'), ('accountant', 'Accountant'), ('inward_manager', 'Inward Manager'), ('admin', 'Admin')], max_length=32),
        ),
    ]