from yoomoney import Quickpay, Client

from webapp.config import YOOMONEY_TOKEN, YOOMONEY_WALLET


def prepare_link_for_payment(payment_sum, order_number) -> Quickpay:
    payment_link = Quickpay(
        receiver=YOOMONEY_WALLET,
        quickpay_form="shop",
        targets=f"Оплата по заказу № {order_number}",
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
