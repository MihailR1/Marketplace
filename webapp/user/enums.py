from enum import Enum


class EmailEventsForUser(Enum):
    hello_letter = 'hello_email_to_user'
    letter_with_account_password = 'letter_with_account_password'
    order_successfully_paid = 'order_successfully_paid'


class UserRole(Enum):
    admin = 'admin'
    user = 'user'
