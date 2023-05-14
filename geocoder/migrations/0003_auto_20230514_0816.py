# Generated by Django 3.2.15 on 2023-05-14 07:32

from django.db import migrations
from django.conf import settings

from geocoder.utils import fetch_coordinates


def copy_restaurant_address_to_address_model(apps, schema_editor):
    Restaurant = apps.get_model('foodcartapp', 'Restaurant')
    Address = apps.get_model('geocoder', 'Address')

    for restaurant in Restaurant.objects.all().iterator():
        address, created = Address.objects.get_or_create(address=restaurant.address)
        if created:
            coordinates = fetch_coordinates(
                settings.GEOCODER_YANDEX_API_KEY,
                address.address
            )
            if coordinates:
                address.latitude, address.longitude = coordinates
                address.save()


def copy_order_address_to_address_model(apps, schema_editor):
    Order = apps.get_model('foodcartapp', 'Order')
    Address = apps.get_model('geocoder', 'Address')

    for order in Order.objects.all().iterator():
        address, created = Address.objects.get_or_create(address=order.address)
        if created:
            coordinates = fetch_coordinates(
                settings.GEOCODER_YANDEX_API_KEY,
                address.address
            )
            if coordinates:
                address.latitude, address.longitude = coordinates
                address.save()


class Migration(migrations.Migration):

    dependencies = [
        ('geocoder', '0002_alter_address_latitude'),
    ]

    operations = [
        migrations.RunPython(copy_restaurant_address_to_address_model),
        migrations.RunPython(copy_order_address_to_address_model),
    ]
