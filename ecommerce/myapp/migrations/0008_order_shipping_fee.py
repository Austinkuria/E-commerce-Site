# Generated by Django 5.1 on 2024-09-06 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0007_alter_profile_address_alter_profile_city_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='shipping_fee',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]