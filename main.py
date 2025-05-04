import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random

from wikipedia import PageError

from config import TOKEN, GROUP_ID
import wikipedia
def main():
    vk_session_bot = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session_bot, GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk_bot = vk_session_bot.get_api()
            try:
                res = wikipedia.summary(event.obj.message["text"], sentences=10)
                vk_bot.messages.send(user_id=event.obj.message["from_id"],
                                     message=f"Что вы хотите узнать?\n{res}",
                                     random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18))
            except PageError:
                vk_bot.messages.send(user_id=event.obj.message["from_id"],
                                     message=f"Что вы хотите узнать?",
                                     random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18))


if __name__ == '__main__':
    wikipedia.set_lang('ru')
    main()
