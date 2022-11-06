from loguru import logger

from webapp.config import UNISENDER_API_KEY, EMAIL_SENDER_NAME, SENDER_EMAIL
from webapp.marketplace.models import ShoppingOrder
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser
from webapp.user.tasks import send_async_email_using_unisender


def send_email(event: EmailEventsForUser, user: User, **kwargs) -> None:
    event_to_email_event_handler_function_mapper = {
        EmailEventsForUser.hello_letter: send_hello_email_to_user_after_registration,
        EmailEventsForUser.order_successfully_paid: send_email_about_successfully_paid_order,
        EmailEventsForUser.letter_with_account_password: send_email_with_generated_password,
    }
    event_to_email_event_handler_function_mapper[event](user, **kwargs)


def send_hello_email_to_user_after_registration(user: User, **kwargs) -> None:
    logger.info('Запустили функцию формирования приветственного email')
    email_subject = 'Подтверждение регистрации на сайте Super1Site'
    email_body = 'Спасибо за регистрацию на нашем сайт'
    user_email = user.email
    prepare_email_for_unisender(user_email, email_subject, email_body)


def send_email_about_successfully_paid_order(user: User, **kwargs) -> None:
    logger.info('Запустили функцию формирования email с уведомлением об успешной оплате')
    shopping_order = ShoppingOrder.query.filter(ShoppingOrder.user_id == user.id).all()[-1]
    email_subject = 'Заказ успешно оплачен'
    email_body = f'Заказ №{shopping_order.order_number} на сумму {shopping_order.amount} руб. успешно оплачен'
    prepare_email_for_unisender(user.email, email_subject, email_body)


def send_email_with_generated_password(user: User, **kwargs) -> None:
    logger.info('Запустили функцию формирования email с данными для входа')
    user_password = kwargs['password']
    email_subject = 'Данные для входа на сайт'
    email_body = f'''Вы успешно зарегистрировались на сайте,<br> 
    чтобы просматривать историю заказов нужно авторизоваться в личном кабинете.<br>
    Почта: {user.email}<br>
    Пароль: {user_password}<br>
    Ссылка на сайт: <a href="https://super1site.ru/users/login">Авторизоваться</a>
    '''
    prepare_email_for_unisender(user.email, email_subject, email_body)


def prepare_email_for_unisender(user_email, email_subject, email_body) -> None:
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
    send_async_email_using_unisender.delay(params_send_email)
