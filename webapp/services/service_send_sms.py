from enum import Enum
from random import randint

import requests
from loguru import logger
import mainsms

from webapp.config import MAINSMS_API, MAINSMS_PROJECT_NAME
from webapp.user.enums import SmsEventsForUser


def generate_six_digits_code() -> str:
    generated_code = ''.join([str(randint(0, 9)) for _ in range(5)])
    return generated_code


def is_sms_delivered(message_id) -> bool:
    sms = mainsms.SMS(MAINSMS_PROJECT_NAME, MAINSMS_API)
    delivery_status = sms.statusSMS(message_id)['messages'][message_id]
    if delivery_status == 'delivered':
        return True

    return False


def send_sms(event, user_phone) -> None:
    event_to_sms_event_handler_func_mapper = {
        SmsEventsForUser.send_auth_sms: send_authentication_sms_code_to_user
    }
    sms_result = event_to_sms_event_handler_func_mapper[event](user_phone)

    if sms_result:
        if sms_result['status'] == 'error':
            logger.info(f'Ошибка во время отправки СМС: Номер {user_phone}, Ошибка {sms_result["message"]}')


def send_authentication_sms_code_to_user(user_phone) -> mainsms.SMS | None:
    generated_code = generate_six_digits_code()
    sms_text = f'Пароль для входа на сайт: {generated_code}'
    sms_result = send_sms_using_mainsms(user_phone, sms_text)

    return sms_result


def send_sms_using_mainsms(user_phone, sms_text) -> mainsms.SMS | None:
    sms = mainsms.SMS(MAINSMS_PROJECT_NAME, MAINSMS_API)
    try:
        status_sent_sms = sms.sendSMS(user_phone, sms_text)
    except requests.RequestException as error:
        logger.exception(f'Ошибка во время отправки смс: {error}')
        status_sent_sms = None

    return status_sent_sms
