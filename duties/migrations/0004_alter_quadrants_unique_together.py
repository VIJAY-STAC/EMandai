# Generated by Django 4.0.2 on 2023-12-31 18:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('duties', '0003_duty_total_outlets'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='quadrants',
            unique_together={('name',)},
        ),
    ]
