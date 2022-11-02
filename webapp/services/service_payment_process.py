import hashlib

from yoomoney import Quickpay, Client

from webapp.config import YOOMONEY_TOKEN, YOOMONEY_WALLET, YOOMONEY_SECRET_KEY


def prepare_link_for_payment(payment_sum, order_number) -> Quickpay:
    payment_link = Quickpay(
        receiver=YOOMONEY_WALLET,
        quickpay_form="shop",
        targets=f"Оплата по заказу №{order_number}",
        paymentType="SB",
        sum=payment_sum,
        label=order_number,
        successURL='http://super1site.ru/payment_status',
    )

    return payment_link.redirected_url


def is_order_paid(order_number) -> bool:
    client = Client(YOOMONEY_TOKEN)
    order_status_from_yoomoney = client.operation_history(label=order_number)

    for operation in order_status_from_yoomoney.operations:
        if operation.status == 'success':
            return True

    return False


def verify_payment(request) -> bool:
    notification_type = request.form["notification_type"]
    operation_id = request.form["operation_id"]
    amount = request.form["amount"]
    currency = request.form["currency"]
    datetime = request.form["datetime"]
    sender = request.form["sender"]
    codepro = request.form["codepro"]
    label = request.form["label"]
    sha1_hash = request.form["sha1_hash"]

    generated_string = f'{notification_type}&{operation_id}&{amount}&{currency}&{datetime}&{sender}&{codepro}&{YOOMONEY_SECRET_KEY}&{label}'
    encoded_generated_string = generated_string.encode()
    hash_from_generated_string = hashlib.sha1(encoded_generated_string)
    hex_value_from_string = hash_from_generated_string.hexdigest()

    if sha1_hash == hex_value_from_string:
        return True

    return False
