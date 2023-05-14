import requests
from geopy import distance


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


def calculate_distance(address_1, address_2, api_key):
    address_1_coords = (fetch_coordinates(api_key, address_1))
    address_2_coords = (fetch_coordinates(api_key, address_2))
    if address_1_coords and address_2_coords:
        return round(distance.distance(address_1_coords, address_2_coords).km, 2)
    return 'Не удалось определить'
