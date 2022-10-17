import requests
from config import Y_TOKEN


def get_data(source, method):
    """VALIDATION ENTERED DATA"""
    geocode = source

    if method == 'region_city':
        request = requests.get(
            f'https://geocode-maps.yandex.ru/1.x/?format=json&apikey={Y_TOKEN}&geocode={geocode}&results=1')

        try:
            result = request.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
                'metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']
            # print(request.json())
            
        except Exception as e:
            result = None
            
        try:
            region = result['AdministrativeAreaName']
        except Exception as e:
            region = None
            
        try:
            city = result['SubAdministrativeArea']['Locality']['LocalityName']
        except Exception as e:
            try:
                city = result['Locality']['LocalityName']
            except Exception as e:
                city = None
            
        return {'region': region, 'city': city}

    elif method == 'all_data':

        request = requests.get(
            f'https://geocode-maps.yandex.ru/1.x/?format=json&apikey={Y_TOKEN}&geocode={geocode}')
        
        try:
            result_address = request.json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject'][
                'metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']
        except Exception as e:
            result_address = None
            
        try:
            result_area = request.json()['response']['GeoObjectCollection']['featureMember'][1]['GeoObject'][
                'metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AdministrativeArea']
            area = result_area['SubAdministrativeArea']['Locality']['DependentLocality']['DependentLocalityName']
        except Exception as e:
            
            try:
                area = result_area['Locality']['DependentLocality']['DependentLocality']['DependentLocalityName']
            except Exception as e:
                try:
                    area = result_area['Locality']['DependentLocality']['DependentLocalityName']
                except Exception as e:
                    area = None
                

        try:
            region = result_address['AdministrativeAreaName']
        except Exception as e:
            region = None


        try:
            city = result_address['SubAdministrativeArea']['Locality']['LocalityName']
        except Exception as e:
            
            try:
                city = result_address['Locality']['LocalityName']
            except Exception as e:
                city = None

        try:
            street = result_address['SubAdministrativeArea']['Locality']['Thoroughfare']['ThoroughfareName']
        except Exception as e:
            
            try:
                street = result_address['Locality']['Thoroughfare']['ThoroughfareName']
            except Exception as e:
                street = None

        try:
            house = result_address['SubAdministrativeArea']['Locality']['Thoroughfare']['Premise']['PremiseNumber']
        except Exception as e:
            try:
                house = result_address['Locality']['Thoroughfare']['Premise']['PremiseNumber']
            except Exception as e:
                house = None

        return {'area': area,
                'region': region,
                'city': city,
                'street': street,
                'house': house}

# print(get_data('Москва, Таганский, Большой Факельный переулок, 24,', 'all_data'))