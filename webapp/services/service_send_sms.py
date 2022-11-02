from random import randrange

import requests
from loguru import logger
from webapp.services import service_mainsms as mainsms

from webapp.config import MAINSMS_API_KEY, MAINSMS_PROJECT_NAME
from webapp.user.enums import SmsEventsForUser
from webapp.user.models import User


def generate_six_digits_code() -> str:
    return randrange(10 ** 6)


def delete_symbols_from_phone_number(phone_number) -> str:
    clear_phone_number = ''.join([digit for digit in phone_number if digit.isdigit()])
    return clear_phone_number


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


def send_authentication_sms_code_to_user(user: User, **kwargs) -> mainsms.SMS | None:
    generated_code = kwargs['generated_code']
    if generated_code:
        sms_text = f'Пароль для входа на сайт: {generated_code}'
        sms_result = send_sms_using_mainsms(user.phone_number, sms_text)

        return sms_result


def send_sms_using_mainsms(user_phone, sms_text) -> mainsms.SMS | None:
    sms = mainsms.SMS(MAINSMS_PROJECT_NAME, MAINSMS_API_KEY)
    try:
        status_sent_sms = sms.sendSMS(user_phone, sms_text, test=0)
    except requests.RequestException as error:
        logger.exception(f'Ошибка во время отправки смс: {error}')
        status_sent_sms = None

    return status_sent_sms
