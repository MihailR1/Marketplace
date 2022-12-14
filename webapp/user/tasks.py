import json

import requests
from loguru import logger

from webapp.celery_app import celery
from webapp.config import SEND_EMAIL_URL


@celery.task(bind=True, retry_backoff=60, max_retries=3)
def send_async_email_using_unisender(self, params_send_email):
    try:
        response = requests.get(SEND_EMAIL_URL, params=params_send_email)
    except requests.RequestException as error:
        logger.exception(f'Ошибка во время отправки email: {error}. Попытка: {self.request.retries} из {self.max_retries}')
        self.retry(exc=error)
        response = None

    if response:
        email_response_checker(response)


def email_response_checker(response):
    try:
        response_serialize = response.json()
    except json.JSONDecodeError as error:
        logger.exception(f'Получен ответ от почтового сервиса с ошибкой: {error}')

    error = response_serialize.get('error', None)
    if error:
        logger.error(f'Ошибка в формировании запроса отправки email: {error}')

    logger.info(f'Письмо успешно отправлено на почту')
