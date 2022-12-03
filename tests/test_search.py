def test_user_search_exist_product(client_with_products):
    formdata = {'search_input': 'БОтинки'}
    response = client_with_products.post('/search', data=formdata, follow_redirects=True)
    assert bytes("По запросу «ботинки» найдено 1", "utf-8") in response.data
    assert response.request.path == '/search'


def test_user_search_unexist_product(client_with_products):
    formdata = {'search_input': 'тапочки'}
    response = client_with_products.post('/search', data=formdata, follow_redirects=True)
    assert bytes("найдено 0 товаров", "utf-8") in response.data
    assert response.request.path == '/search'


def test_livesearch_return_list_with_found_products(client_with_products):
    formdata = {'search': 'Женская Куртка'}
    response = client_with_products.post('/livesearch', data=formdata)
    assert response.json[0][0] == 'Розовая женская куртка Armani'


def test_livesearch_return_list_with_not_found_products(client_with_products):
    formdata = {'search': 'велосипед'}
    response = client_with_products.post('/livesearch', data=formdata)
    assert not response.json
