from flask import session
from flask_login import current_user

from webapp.user.models import User


def test_registration_and_login_page_is_available(client):
    response = client.get('/users/login_register')
    assert response.status_code == 200


def test_correct_login_user(client_with_user):
    formdata = {'email': 'test@gmail.com', 'password': 'testing'}
    response = client_with_user.post('/users/process-login', data=formdata, follow_redirects=True)
    assert current_user.email == 'test@gmail.com'
    assert bytes("Вы успешно вошли на сайт", "utf-8") in response.data


def test_logout_user(client_with_user):
    response = client_with_user.get("/users/logout", follow_redirects=True)
    assert not current_user.is_authenticated
    assert bytes("Вы успешно вышли из сайта", "utf-8") in response.data


def test_correct_registration_new_user(client):
    formdata = {'email': 'test2@gmail.com', 'password': 'testing3', 'password2': 'testing3'}
    response = client.post('/users/process_reg', data=formdata, follow_redirects=True)
    assert current_user.is_authenticated
    assert bytes("Вы успешно зарегистрировались и авторизовались", "utf-8") in response.data
    assert User.query.filter(User.email == 'test2@gmail.com').count() == 1


def test_registration_with_exist_email(client_with_user):
    formdata = {'email': 'test@gmail.com', 'password': 'testing'}
    response = client_with_user.post('/users/process_reg', data=formdata, follow_redirects=True)
    assert bytes("Пользователь с таким адресом уже существует", "utf-8") in response.data
    assert response.request.path == '/users/login_register'


def test_registration_with_different_passwords(client):
    formdata = {'email': 'test255@gmail.com', 'password': 'AnyRandomPass22', 'password2': 'AnyRandomPass21'}
    response = client.post('/users/process_reg', data=formdata, follow_redirects=True)
    assert response.request.path == '/users/login_register'
    assert b"Field must be equal to password" in response.data


def test_login_user_with_wrong_password(client_with_user):
    formdata = {'email': 'test@gmail.com', 'password': 'WrongPasswrd'}
    response = client_with_user.post('/users/process-login', data=formdata, follow_redirects=True)
    assert bytes("Не правильные имя или пароль", "utf-8") in response.data


def test_login_user_with_wrong_email(client_with_user):
    formdata = {'email': 'WrongEmail@gmail.com', 'password': 'testing'}
    response = client_with_user.post('/users/process-login', data=formdata, follow_redirects=True)
    assert bytes("Не правильные имя или пароль", "utf-8") in response.data


def test_user_input_correct_phone_in_sms_auth_page(client):
    formdata = {'phone_number': '79999999999'}
    response = client.post('/users/process_auth_sms', data=formdata, follow_redirects=True)
    assert bytes("СМС с кодом отправлено", "utf-8") in response.data


def test_user_login_with_correct_sms_code(client):
    data_for_send_sms = {'phone_number': '79999999995'}
    with client:
        client.post('/users/process_auth_sms', data=data_for_send_sms, follow_redirects=True)
        generated_sms_code = session.get('sms_code', None)
        client.post('/users/check_sms', data={'user_code': generated_sms_code})
        assert current_user.phone_number == "79999999995"


def test_user_login_with_wrong_sms_code(client):
    data_for_send_sms = {'phone_number': '79999999993'}
    with client:
        client.post('/users/process_auth_sms', data=data_for_send_sms, follow_redirects=True)
        client.post('/users/check_sms', data={'user_code': '783635'})
        assert not current_user.is_authenticated


def test_user_edit_profile(client_with_loggined_user):
    new_user_data = {'phone_number': '79995949999', 'full_name': 'New_name',
                     'shipping_adress': 'Москва, Тверская 40'}
    response = client_with_loggined_user.post('/users/process_update_data_user', data=new_user_data,
                                              follow_redirects=True)
    assert bytes("Вы успешно изменили свои данные", "utf-8") in response.data
    assert current_user.phone_number == new_user_data['phone_number']
    assert current_user.full_name == new_user_data['full_name']
    assert current_user.shipping_adress == new_user_data['shipping_adress']
