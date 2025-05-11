import vk_api
from flask import Flask, render_template
from vk_api import ApiError
from werkzeug.exceptions import BadRequest

from config import PASSWORD, LOGIN

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


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


@app.route('/vk_stat/<int:group_id>')
def admin_page(group_id):
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
    vk = vk_session.get_api()

    try:
        res = vk.stats.get(group_id=group_id, intervals_count=10, extended=True)[0]
    except ApiError:
        return BadRequest()

    try:
        cities = list(set([x['name'] for x in res['visitors']['cities']]))
    except KeyError:
        cities = []

    activities = {}
    for x in ['likes', 'comments', 'subscribed']:
        try:
            activities[x] = res['activity'][x]
        except KeyError:
            activities[x] = 0

    try:
        ages_j = res['reach']['age']
    except KeyError:
        ages_j = {}
    ages = {}
    for n, x in enumerate(['12-18', '18-21', '21-24', '24-27', '27-30', '30-35', '35-45', '45-100']):
        try:
            ages[x] = ages_j[n]['count']
        except KeyError:
            ages[x] = 0
    return render_template('index.html', cities=cities, activities=activities, ages=ages)


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')
