import random
from datetime import datetime

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
            try:
                new_date = datetime.strptime(event.obj.message['text'], '%Y-%m-%d')
                vk.messages.send(user_id=event.obj.message["from_id"],
                                 message=DAYS_WEEK[new_date.weekday()],
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18))
            except ValueError:
                vk.messages.send(user_id=event.obj.message["from_id"],
                                 message=f"Вы можете узнать день недели, введя дату в формате YYYY-MM-DD",
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18))


if __name__ == '__main__':
    main()
