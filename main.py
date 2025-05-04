import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
import random
from config import TOKEN, GROUP_ID, ALBUM_ID, LOGIN, PASSWORD
from random import choice


def captcha_handler(captcha):
    """ При возникновении капчи вызывается эта функция и ей передается объект
        капчи. Через метод get_url можно получить ссылку на изображение.
        Через метод try_again можно попытаться отправить запрос с кодом капчи
    """

    key = input("Enter captcha code {0}: ".format(captcha.get_url())).strip()

    # Пробуем снова отправить запрос с капчей
    return captcha.try_again(key)


def auth_handler():
    """ При двухфакторной аутентификации вызывается эта функция. """

    # Код двухфакторной аутентификации,
    # который присылается по смс или уведомлением в мобильное приложение
    # или код из приложения - генератора кодов
    key = input("Enter authentication code: ")
    # Если: True - сохранить, False - не сохранять.
    remember_device = True

    return key, remember_device


def main():
    login, password = LOGIN, PASSWORD
    vk_session = vk_api.VkApi(
        login, password,
        # функция для обработки двухфакторной аутентификации
        auth_handler=auth_handler,
        captcha_handler=captcha_handler
    )

    try:
        vk_session.auth(token_only=True)
    except vk_api.AuthError as error_msg:
        print(error_msg)
        return
    vk_session_bot = vk_api.VkApi(
        token=TOKEN)

    longpoll = VkBotLongPoll(vk_session_bot, GROUP_ID)

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW:
            vk = vk_session.get_api()
            user = vk.users.get(user_ids=[event.obj.message["from_id"]], fields="city")[0]
            name = user["first_name"]
            photo = choice(vk.photos.get(album_id=ALBUM_ID, group_id=GROUP_ID)['items'])
            vk_bot = vk_session_bot.get_api()
            vk_bot.messages.send(user_id=user['id'],
                                 message=f"Привет, {name}!",
                                 random_id=random.randint(-9 * 10 ** 18, 9 * 10 ** 18),
                                 attachment=f'photo{photo["owner_id"]}_{photo["id"]}')


if __name__ == '__main__':
    main()
