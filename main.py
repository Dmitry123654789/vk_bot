import random
from datetime import datetime, timezone, timedelta

import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType

from config import TOKEN, GROUP_ID

DAYS_WEEK = ['Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье']


def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            if any(text in event.obj.message['text'].lower() for text in ["время", "число", "дата", "день"]):
                offset = timezone(timedelta(hours=3))
                vk.messages.send(user_id=event.obj.message["from_id"],
                                 message=datetime.now(offset).strftime(
                                     f'%Y-%m-%d %H:%M:%S {DAYS_WEEK[datetime.now(offset).weekday()]}'),
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18))
            else:
                vk.messages.send(user_id=event.obj.message["from_id"],
                                 message="Вы можете узнать сегодняшнюю дату, московское время и день недели, введя одно из этих слов в своем сообщении «время», «число», «дата», «день»",
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18))


if __name__ == '__main__':
    main()
