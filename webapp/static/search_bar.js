$(document).ready(function () {
    var $result = $('#search_box-result');

    function query_to_db(data, user_query) {
        if (data != '') {
            $result.html('').show();
            for (var i in data) {
                let addBoldText = `${data[i][0].toLowerCase()}`.replace(user_query.toLowerCase(), `<b>${user_query.toLowerCase()}</b>`)
                $result.append(
                    $(
                        '<div class="search_result_sub">' +
                        '<div class="search_result-name">' +
                        '<a href="/product/' + data[i][1] + '" >' + addBoldText + '</a>' +
                        '</div>' +
                        '</div>'
                    )
                );
                $result.fadeIn();
            }
        } else {
            $result.fadeOut(100);
        }
    }

    $('#search_input').on('keyup', function () {
        var search = $(this).val();
        if ((search != '') && (search.length > 2)) {
            $.ajax({
                type: "POST",
                url: "/livesearch",
                data: {'search': search},
                success: function (msg) {
                    query_to_db(msg, search);
                }
            });
        } else {
            $result.html('');
            $result.fadeOut(100);
        }
    });

    // Скрывает подсказки при клике за пределами области подсказок
    $(document).on('click', function (e) {
        if (!$(e.target).closest('.search_box').length) {
            $result.html('');
            $result.fadeOut(100);
        }
    });

});
