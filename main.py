import random
from json import loads
from os import remove

import requests
import vk_api
from requests.adapters import HTTPAdapter
from urllib3 import Retry
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config import TOKEN, GROUP_ID

LAST_MES = ''
LAST_COM = ''


def get_json(adress):
    api_key = '8013b162-6b42-4997-9691-77b7074026e0'
    server_address = 'https://geocode-maps.yandex.ru/1.x/?'
    geocoder_request = f'{server_address}apikey={api_key}&geocode={adress}&format=json'
    response = requests.get(geocoder_request)
    return response


def get_response_map(ll):
    server_address = "https://static-maps.yandex.ru/v1"
    apikey = '0eea7a3e-806e-4b45-8976-3c543752e89c'
    map_params = {
        'll': ll,
        'apikey': apikey,
        'maptype': LAST_COM,
        'z': 15,
        'lang': 'ru_RU'
    }
    session = requests.Session()
    retry = Retry(total=10, connect=5, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    response = requests.get(server_address, params=map_params)
    return response


def main():
    global LAST_MES, LAST_COM
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    for event in longpoll.listen():

        if event.type == VkBotEventType.MESSAGE_NEW:
            try:
                if LAST_COM == 'type':
                    LAST_COM = loads(event.object['message']['payload'])['command']
            except KeyError:
                LAST_COM = ''

            vk = vk_session.get_api()
            if LAST_COM == '':
                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message="Что вы хотите увидеть?",
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18),
                                 keyboard='{"one_time": false, "buttons": []}')
                LAST_COM = 'que'

            elif LAST_COM == 'que':
                LAST_MES = event.object.message['text']

                try:
                    res = get_json(LAST_MES).json()['response']['GeoObjectCollection']['featureMember']
                    if len(res) == 0:
                        LAST_COM = 'que'
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="Что вы хотите увидеть?",
                                         random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18),
                                         keyboard='{"one_time": false, "buttons": []}')
                    else:
                        vk.messages.send(user_id=event.obj.message['from_id'],
                                         message="Какой тип карты вы хотите увидеть?",
                                         random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18),
                                         keyboard=open('buttons.json', encoding='utf-8').read())
                        LAST_COM = 'type'
                except Exception as e:
                    vk.messages.send(user_id=event.obj.message['from_id'],
                                     message="Повторите запрос.\nЧто вы хотите увидеть",
                                     random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18),
                                     keyboard='{"one_time": false, "buttons": []}')
                    LAST_COM = 'que'


            elif LAST_COM in ['admin', 'transit', 'driving', 'map']:
                res = get_json(LAST_MES).json()['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']
                poi = ','.join(res['Point']['pos'].split(' '))
                place = res['metaDataProperty']['GeocoderMetaData']['AddressDetails']['Country']['AddressLine']

                open('map.png', 'wb').write(get_response_map(poi).content)
                upload = vk_api.VkUpload(vk_session)
                photo = upload.photo_messages(photos='map.png')[0]
                attachment = f"photo{photo['owner_id']}_{photo['id']}"
                remove("map.png")

                vk.messages.send(user_id=event.obj.message['from_id'],
                                 message=f'Это {place}. Что вы еще хотите увидеть?',
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18),
                                 attachment=attachment,
                                 keyboard='{"one_time": false, "buttons": []}')
                LAST_COM = 'que'


if __name__ == '__main__':
    main()
