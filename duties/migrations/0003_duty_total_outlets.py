# Generated by Django 4.0.2 on 2023-12-31 17:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('duties', '0002_routes_areas'),
    ]

    operations = [
        migrations.AddField(
            model_name='duty',
            name='total_outlets',
            field=models.IntegerField(default=0),
        ),
    ]
