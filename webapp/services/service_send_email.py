import requests
from enum import Enum

from webapp.config import UNISENDER_KEY, SEND_EMAIL_URL, EMAIL_SENDER_NAME, SENDER_EMAIL


class EmailLetter(Enum):
    def send_hello_email_to_user(self):
        email_subject = 'Подарочный купон Super1Site'
        email_body = 'Спасибо за регистрацию на нашем сайт'
        user_email = self
        return send_email_to_user(user_email, email_subject, email_body)


def send_email_to_user(user_email, email_subject, email_body, user_name=None):
    email_unsubscribe_id = 1
    params_send_email = {
        'format': 'json',
        'api_key': UNISENDER_KEY,
        'sender_name': EMAIL_SENDER_NAME,
        'sender_email': SENDER_EMAIL,
        'list_id': email_unsubscribe_id,
        'email': user_email,
        'subject': email_subject,
        'body': email_body,
    }

    try:
        response = requests.get(SEND_EMAIL_URL, params=params_send_email)
        result = response.json()
        error = result.get('error', None)
        if error:
            return error
    except Exception as error:
        return error

    return True


def email_handler(enum_event, user_handler):
    print(enum_event)
    try:
        enum_event(user_handler)
        print('Success')
    except (ValueError, requests.exceptions.RequestException, requests.exceptions.ConnectionError) as err:
        print('Принт ошибки')
        print(err)


email_handler(EmailLetter.send_hello_email_to_user, 'MihailR.20@yandex.ru')

