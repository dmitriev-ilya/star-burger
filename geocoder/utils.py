from django.conf import settings
import requests
from geopy import distance

from geocoder.models import Address


def fetch_coordinates(apikey, address):
    base_url = "https://geocode-maps.yandex.ru/1.x"
    response = requests.get(base_url, params={
        "geocode": address,
        "apikey": apikey,
        "format": "json",
    })
    response.raise_for_status()
    found_places = response.json()['response']['GeoObjectCollection']['featureMember']

    if not found_places:
        return None

    most_relevant = found_places[0]
    lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
    return lat, lon


def calculate_distance(address_1, address_2):
    if address_1.latitude and address_2.latitude:
        address_1_coords = (address_1.latitude, address_1.longitude)
        address_2_coords = (address_2.latitude, address_2.longitude)
        return round(distance.distance(address_1_coords, address_2_coords).km, 2)
    return 'Не удалось определить'


def create_address(address):
    address, created = Address.objects.get_or_create(address=address)
    if created:
        coordinates = fetch_coordinates(
            settings.GEOCODER_YANDEX_API_KEY,
            address.address
        )
        if coordinates:
            address.latitude, address.longitude = coordinates
            address.save()
            return
