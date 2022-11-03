import json

from loguru import logger

from webapp.celery_app import celery
from webapp.services.service_send_sms import send_authentication_sms_code_to_user
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser, SmsEventsForUser
from webapp.services.service_send_email import (send_hello_email_to_user_after_registration,
                                                send_email_about_successfully_paid_order,
                                                send_email_with_generated_password)


@celery.task
def send_email(event: EmailEventsForUser, user: User, **kwargs) -> None:
    event_to_email_event_handler_function_mapper = {
        EmailEventsForUser.hello_letter: send_hello_email_to_user_after_registration,
        EmailEventsForUser.order_successfully_paid: send_email_about_successfully_paid_order,
        EmailEventsForUser.letter_with_account_password: send_email_with_generated_password,
    }
    response = event_to_email_event_handler_function_mapper[event](user, **kwargs)

    if response:
        try:
            response_serialize = response.json()
        except json.JSONDecodeError as error:
            logger.exception(f'Получен ответ от почтового сервиса с ошибкой: {error}')

        error = response_serialize.get('error', None)
        if error:
            logger.error(f'Ошибка в формировании запроса отправки email: {error}')

        logger.info(f'Письмо успешно отправлено на почту: {user.email}')


@celery.task
def send_sms(event, user: User, **kwargs) -> bool:
    event_to_sms_event_handler_func_mapper = {
        SmsEventsForUser.send_auth_sms: send_authentication_sms_code_to_user
    }
    response = event_to_sms_event_handler_func_mapper[event](user, **kwargs)

    if response:
        if response['status'] == 'success':
            logger.info(f'СМС успешно отправлено на номер: {user.phone_number}')
            return True
        else:
            logger.info(f'Ошибка во время отправки СМС: Номер {user.phone_number}, Ошибка {response["message"]}')

    return False


@celery.task
def add(x, y):
    print(x + y)