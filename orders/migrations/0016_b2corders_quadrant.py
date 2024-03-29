# Generated by Django 4.0.2 on 2024-01-01 05:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('duties', '0005_alter_routes_unique_together'),
        ('orders', '0015_b2corders_duty'),
    ]

    operations = [
        migrations.AddField(
            model_name='b2corders',
            name='quadrant',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='order_quadrant', to='duties.quadrants'),
        ),
    ]
