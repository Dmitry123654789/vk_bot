import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from config import TOKEN, GROUP_ID

def main():
    vk_session = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session, GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            user = vk.users.get(user_ids=[event.obj.message["from_id"]], fields="city, bdate, country")[0]
            city = user["city"]['title'] if "city" in user else None
            name = user["first_name"]

            vk.messages.send(user_id=user['id'],
                             message=f"Привет, {name}!",
                             random_id=random.randint(-9*10**18, 9*10**18))
            if city:
                vk.messages.send(user_id=user['id'],
                                 message=f"Как поживает {city}?",
                                 random_id=random.randint(-9*10**18, 9*10**18))


if __name__ == '__main__':
    main()
