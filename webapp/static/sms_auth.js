function check_sms_status() {
    let response = fetch('/process_auth_sms', {
        method: 'POST',
        mode: 'cors',
        cache: 'no-cache',
        credentials: 'same-origin',
        headers: {'Content-Type': 'application/json', 'charset': 'UTF-8'},
        redirect: 'follow',
        referrerPolicy: 'no-referrer'
    }).then((response) => {
        if (response.status == "200") {
            console.log('Response 200')
            return response.json()
        }
    }).then(response_info => {
        if (response_info['is_sms_sent'] == true) {
            console.log('okokok')
            document.getElementById('payment_status_text').innerText = 'Платеж выполнен\n' +
                'Перенаправляем на главную страницу сайта';

            setTimeout(function () {
                window.location.href = '/';
            }, 2 * 1000);

        } else {
            console.log('Not sent')
            setInterval(function () {
                check_payment();
            }, 3000);
        }
    });
}

document.querySelector('phone_auth_form').addEventListener('submit', (event) => {
console.log('Отправка формы')
})
