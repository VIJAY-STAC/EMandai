# Generated by Django 4.0.2 on 2023-12-31 18:48

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('duties', '0004_alter_quadrants_unique_together'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='routes',
            unique_together={('pincode', 'quadrant')},
        ),
    ]
