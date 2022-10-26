from random import randint

from yoomoney import Quickpay, Client

from webapp.config import YOOMONEY_TOKEN, YOOMONEY_WALLET


orders_number_list = []


def generate_order_number() -> str:
    order_number = ''
    for number in range(25):
        order_number += str(randint(0, 9))

    if order_number not in orders_number_list:
        orders_number_list.append(order_number)
        return order_number
    else:
        return generate_order_number()


def prepare_link_for_payment(payment_sum, order_number) -> Quickpay:
    payment_link = Quickpay(
        receiver=YOOMONEY_WALLET,
        quickpay_form="shop",
        targets=f"Оплата по заказу № {order_number}",
        paymentType="SB",
        sum=payment_sum,
        label=order_number,
    )

    return payment_link.redirected_url


def is_order_paid(order_number, order_amount) -> bool:
    client = Client(YOOMONEY_TOKEN)
    order_status_from_yoomoney = client.operation_history(label=order_number)

    for operation in order_status_from_yoomoney.operations:
        if operation.status == 'success' and operation.amount == order_amount:
            return True

    return False
