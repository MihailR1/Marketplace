from enum import Enum


class EmailEventsForUser(Enum):
    hello_letter = 'hello_email_to_user'


class SmsEventsForUser(Enum):
    send_auth_sms = 'send_authentication_sms_code_to_user'
