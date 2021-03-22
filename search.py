import argparse
import os

import requests
from PIL import Image
from io import BytesIO

from scale_selection import get_toponym_scale


def search_object(obj: str, size: list, apikey: str):
    geocode_url = 'http://geocode-maps.yandex.ru/1.x/'
    geocode_error_msg = 'Не удалось найти объект на карте'
    static_url = 'http://static-maps.yandex.ru/1.x/'
    static_error_msg = 'Не удалось получить изображение объекта на карте'

    response = requests.get(geocode_url, params={'geocode': obj,
                                                 'format': 'json',
                                                 'apikey': apikey})

    if response.status_code != 200:
        return geocode_error_msg
    data = response.json()['response']
    results = data['GeoObjectCollection']['featureMember']
    if not results:
        return geocode_error_msg
    toponym = results[0]['GeoObject']
    toponym_coords = ','.join(toponym['Point']['pos'].split())
    if not size:
        size = map(str, get_toponym_scale(toponym))
    response = requests.get(static_url, params={'ll': toponym_coords,
                                                'l': 'map',
                                                'spn': ','.join(size),
                                                'pt': '%s,pm2rdm' % toponym_coords})
    if response.status_code != 200:
        return static_error_msg
    Image.open(BytesIO(response.content)).show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('obj', nargs='*', help='Object that is needed to be found on the map')
    parser.add_argument('--size', nargs=2, help='The size of the object in degrees')
    args = parser.parse_args()

    callback = search_object(' '.join(args.obj), args.size, os.getenv('GEOCODE_APIKEY'))
    if callback:
        print(callback)