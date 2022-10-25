import json

import requests
from loguru import logger

from webapp.config import UNISENDER_API_KEY, SEND_EMAIL_URL, EMAIL_SENDER_NAME, SENDER_EMAIL
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser


def send_email(event: EmailEventsForUser, user: User) -> None:
    event_to_email_event_handler_function_mapper = {
        EmailEventsForUser.hello_letter: send_hello_email_to_user_after_registration
    }
    response = event_to_email_event_handler_function_mapper[event](user)

    if response:
        try:
            response_serialize = response.json()
        except json.JSONDecodeError as error:
            logger.exception(f'Получен ответ с ошибкой: {error}')

        error = response_serialize.get('error', None)
        if error:
            logger.error(f'Ошибка в формировании запроса: {error}')

        logger.info(f'Письмо успешно отправлено на почту: {user.email}')


def send_hello_email_to_user_after_registration(user: User) -> requests.Response | None:
    email_subject = 'Подарочный купон Super1Site'
    email_body = 'Спасибо за регистрацию на нашем сайт'
    user_email = user.email
    response = send_email_using_unisender(user_email, email_subject, email_body)
    return response


def send_email_using_unisender(user_email, email_subject, email_body) -> requests.Response | None:
    email_unsubscribe_id = 1
    params_send_email = {
        'format': 'json',
        'api_key': UNISENDER_API_KEY,
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
