import os

import requests
from dotenv import load_dotenv

load_dotenv()

API = os.environ['UNISENDER_API']
SEND_EMAIL_URL = 'https://api.unisender.com/ru/api/sendEmail'

sender_name = 'Интернет Магазин SuperSite'
sender_email = 'no-reply@super1site.ru'
email_unsubscribe_id = 1
email_subject = 'Подарочный купон Super1Site'
email_body = 'Спасибо за регистрацию на нашем сайт'


def send_hello_email_to_user(user_email):
    user_email = user_email
    params_send_email = {
        'format': 'json',
        'api_key': API,
        'email': user_email,
        'sender_name': sender_name,
        'sender_email': sender_email,
        'subject': email_subject,
        'body': email_body,
        'list_id': email_unsubscribe_id
    }
    is_email_send = True
    try:
        response = requests.get(SEND_EMAIL_URL, params=params_send_email)
        result = response.json()
        if result.get('error', None):
            is_email_send = False
    except (ValueError, requests.JSONDecodeError):
        is_email_send = False
    except requests.exceptions.RequestException:
        is_email_send = False

    return is_email_send
