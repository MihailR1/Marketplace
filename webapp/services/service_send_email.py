import json

import requests
from enum import Enum
from loguru import logger

from webapp.config import UNISENDER_KEY, SEND_EMAIL_URL, EMAIL_SENDER_NAME, SENDER_EMAIL
from webapp.user.models import User

logger.add('../logs/service_send_emails.log', format='[{time:YYYY-MM-DD HH:mm:ss}] [{level}] |  {message}',
           level='WARNING')


class EmailLetter(Enum):
    hello_letter = 'send_hello_email_to_user'


def send_email(event: EmailLetter, user: User) -> None:
    event_to_email_letter_enum = {EmailLetter.hello_letter: hello_email_to_user}
    response = event_to_email_letter_enum[event](user)

    if response:
        try:
            response = response.json()
            error = response.get('error', None)
            if error:
                logger.error(f'Ошибка в формировании запроса: {error}')
            logger.info(f'Успешно отправили письмо {user.email}')
        except json.JSONDecodeError as error:
            logger.exception(f'Получен ответ с ошибкой: {error}')


def hello_email_to_user(user_handler: User) -> requests.Response | None:
    email_subject = 'Подарочный купон Super1Site'
    email_body = 'Спасибо за регистрацию на нашем сайт'
    user_email = user_handler.email
    response = send_email_using_service(user_email, email_subject, email_body)
    return response


def send_email_using_service(user_email, email_subject, email_body, user_name=None) -> requests.Request | None:
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
    except requests.RequestException as error:
        logger.exception(f'Ошибка во время запроса: {error}')
        response = None
    return response
