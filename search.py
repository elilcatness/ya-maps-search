import argparse
import requests
from io import BytesIO
from PIL import Image


def search_object(obj: str, size: list, geo_apikey: str, search_apikey: str):
    geocode_url = 'http://geocode-maps.yandex.ru/1.x/'
    geocode_error_msg = 'Не удалось найти объект на карте'
    static_url = 'http://static-maps.yandex.ru/1.x/'
    static_error_msg = 'Не удалось получить изображение объекта на карте'
    search_url = 'https://search-maps.yandex.ru/v1/'

    response = requests.get(geocode_url, params={'geocode': obj,
                                                 'format': 'json',
                                                 'apikey': geo_apikey})

    if response.status_code != 200:
        return geocode_error_msg
    data = response.json()['response']
    results = data['GeoObjectCollection']['featureMember']
    if not results:
        return geocode_error_msg
    toponym = results[0]['GeoObject']
    toponym_coords = ','.join(toponym['Point']['pos'].split())

    pharmacy_error_msg = 'Не удалось найти ближайшую аптеку'
    pharmacy_response = requests.get(search_url, params={'ll': toponym_coords,
                                                         'format': 'json',
                                                         'text': 'аптека',
                                                         'lang': 'ru_RU',
                                                         'type': 'biz',
                                                         'apikey': search_apikey})
    if pharmacy_response.status_code != 200:
        return pharmacy_error_msg
    data = pharmacy_response.json()
    results = data['features']
    if not results:
        return pharmacy_error_msg
    pharmacies = []
    for ph in results:
        ph_coords = ','.join(map(str, ph['geometry']['coordinates']))
        metadata = ph['properties']['CompanyMetaData']
        if 'Hours' not in metadata.keys():
            color = 'gr'
        elif metadata['Hours'].get('Availabilities'):
            color = 'gn' if any(map(lambda x: x.get('TwentyFourHours', False),
                                    metadata['Hours']['Availabilities'])) else 'bl'
        else:
            color = 'gr'
        pharmacies.append('%s,pm2%sm' % (ph_coords, color))

    static_params = {'ll': toponym_coords,
                     'l': 'map',
                     'pt': '~'.join(['%s,pm2rdm' % toponym_coords] + pharmacies)}
    if size:
        static_params['spn'] = ','.join(size)
    response = requests.get(static_url, params=static_params)
    if response.status_code != 200:
        return static_error_msg
    Image.open(BytesIO(response.content)).show()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('obj', nargs='*', help='Object that is needed to be found on the map')
    parser.add_argument('--size', nargs=2, help='The size of the object in degrees')
    args = parser.parse_args()

    callback = search_object(' '.join(args.obj), args.size,
                             '40d1649f-0493-4b70-98ba-98533de7710b',
                             'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3')
    if callback:
        print(callback)
