function check_payment() {
    let response = fetch('/check_payment', {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json', 'charset': 'UTF-8'},
        redirect: 'follow',
        referrerPolicy: 'no-referrer'
    }).then((response) => {
        if (response.status == "200") {
            return response.json()
        }
    }).then(response_info => {
        if (response_info['payment_status'] == true) {
            document.getElementById('payment_status_text').innerText = 'Платеж выполнен\n' +
                'Перенаправляем на главную страницу сайта';

            setTimeout(function () {
                window.location.href = '/';
            }, 2 * 1000);

        } else {
            setInterval(function () {
                check_payment();
            }, 3000);
        }
    });
}

document.onload = check_payment()
