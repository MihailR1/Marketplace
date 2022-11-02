$(document).ready(function () {

    $('#sms_confirm_code_by_user').on('keyup', function () {
        var search = $(this).val();
        if ((search != '') && (search.length == 6)) {

            $.ajax({
                type: "POST",
                url: "/users/check_sms",
                data: {'user_code': search},
                success: function (server_answer) {

                    if (server_answer['is_sms_sent'] == true) {

                        if (server_answer['is_user_answer_right'] == false) {
                            document.getElementById('text_for_sms_confirm').innerText = 'Код не верный, введите другие цифры';
                        } else {
                            document.getElementById('text_for_sms_confirm').innerText = 'Код верный, авторизуем';

                            setTimeout(function () {
                                window.location.href = '/';
                            }, 3 * 1000);
                        }
                    }
                }
            });
        }
    });

});
