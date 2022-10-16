function deleteFromCart(product_id) {
    query_to_db(product_id, 0)
    document.getElementById('cart_product_' + product_id).style.display = 'none';
    console.log('Удаление из корзины')
}

function addToCart(product_id, quantity = 1) {
    document.getElementById('add_to_basket_' + product_id).style.display = 'block';
    document.getElementById('button_add_to_cart_' + product_id).style.display = 'none';
    query_to_db(product_id, quantity)

// Отслеживает изменения в текстовом поле
    $('body').on('change', '#number-text_' + product_id, function () {
        var $input = $(this);
        let $card_id = $('#number-text_' + product_id)
        var $row = $input.closest($card_id);
        var step = $row.data('step');
        var val = parseFloat($input.val());
        if (val == 0) {
            document.getElementById('add_to_basket_' + product_id).style.display = 'none';
            document.getElementById('button_add_to_cart_' + product_id).style.display = 'block';
        }
        if (isNaN(val)) {
            val = step;
        }
        $input.val(val);
        query_to_db(product_id, val)
        if (val == 0) {
            $input.val(1);
        }
    });
}

function query_to_db(product_id, quantity) {
    let response = fetch('/add_to_cart', {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json', 'charset': 'UTF-8'},
        redirect: 'follow',
        referrerPolicy: 'no-referrer',
        body: JSON.stringify({"product_id": product_id, "quantity": quantity})
    }).then((response) => {
        if (response.status == "200") {
            return response.json()
        }
    }).then(response_info => {
        if (response_info['is_available'] == false) {
            document.getElementById('productOut_' + product_id).style.display = 'block';
            document.getElementById('number-text_' + product_id).value = response_info['quantity'];
        }
        document.getElementById('cart_icon').textContent = 'Корзина (' + response_info['unique_products'] + ')'
    });
}
