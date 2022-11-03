from flask import Blueprint, flash, render_template, redirect, url_for, jsonify, session, request, Markup
from flask_login import current_user, login_user, logout_user, login_required

from webapp.db import db
from webapp.user.forms import LoginForm, RegistrationForm, SmsAuthForm, UpdateDataProfileUserForm
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser, SmsEventsForUser, UserRole
from webapp.user.tasks import send_email, send_sms
from webapp.services.service_send_sms import delete_symbols_from_phone_number, generate_six_digits_code
from webapp.services.service_redirect_utils import redirect_back
from webapp.services.service_cart import save_products_into_db_from_session_cart

blueprint = Blueprint('user', __name__, url_prefix='/users')


@blueprint.route('/login_register')
def login_or_register_user():
    if current_user.is_authenticated:
        return redirect_back()

    title_login = "Войти"
    form_login = LoginForm()

    title_register = "Регистрация"
    form_register = RegistrationForm()

    return render_template(
        'user/login_register.html',
        title_login=title_login,
        title_register=title_register,
        form_login=form_login,
        form_register=form_register,
    )


@blueprint.route('/process-login', methods=['POST'])
def process_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            save_products_into_db_from_session_cart(user)

            full_name = session.get('full_name', None)
            shipping_adress = session.get('shipping_adress', None)
            phone_number = session.get('phone_number', None)
            user_email = session.get('email', None)

            if not user.full_name and full_name:
                user.full_name = full_name
            if not user.shipping_adress and shipping_adress:
                user.shipping_adress = shipping_adress
            if not user.phone_number and phone_number:
                user.phone_number = phone_number
            if not user.email and user_email:
                user.email = user_email

            db.session.commit()
            flash("Вы успешно вошли на сайт")
            return redirect_back()

        flash('Не правильные имя или пароль')
        return redirect(url_for('user.login_or_register_user'))


@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из сайта')
    return redirect(url_for('marketplace.index'))


@blueprint.route('/process_reg', methods=['POST'])
def process_reg():
    form = RegistrationForm()

    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            role=UserRole.user
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались')
        send_email.delay(EmailEventsForUser.hello_letter, new_user)
        return redirect(url_for('marketplace.index'))

    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash("Ошибка в поле {}: {}".format(
                    getattr(form, field).label.text,
                    error
                ))
    return redirect(url_for('user.login_or_register_user'))


@login_required
@blueprint.route('/profile_user')
def profile_user():
    title = 'Профиль пользователя'
    user_all_info = User.query.filter(User.id == current_user.id)
    return render_template(
        'user/profile_user.html',
        title=title,
        user_all_info=user_all_info,
    )


@login_required
@blueprint.route('/edit_profile_user')
def edit_profile_user():
    title = 'Редактирование профиля'
    form = UpdateDataProfileUserForm()
    return render_template(
        'user/edit_profile_user.html',
        title=title,
        form=form,
    )


@login_required
@blueprint.route('/process_update_data_user', methods=['POST'])
def process_update_data_user():
    form = UpdateDataProfileUserForm()

    if form.validate_on_submit():
        update_data_user = User.query.get(current_user.id)
        update_data_user.phone_number = form.phone_number.data
        update_data_user.full_name = form.full_name.data
        update_data_user.shipping_adress = form.shipping_adress.data
        db.session.commit()
        flash('Вы успешно изменили свои данные')
        return redirect(url_for('user.profile_user'))
    else:
        flash("Чтобы изменить свои данные, необходимо авторизоваться или зарегистрироваться")
        return redirect(request.referrer)


@blueprint.route('/sms_auth')
def sms_auth():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace.index'))

    title = "Регистрация и авторизация по коду из смс"
    form = SmsAuthForm()
    return render_template('user/sms_auth.html', page_title=title, form=form)


@blueprint.route('/process_auth_sms', methods=['POST'])
def process_auth_sms():
    form_phone_number = SmsAuthForm()

    if form_phone_number.validate_on_submit():
        phone_number = delete_symbols_from_phone_number(form_phone_number.phone_number.data)
        user = User.query.filter(User.phone_number == phone_number).first()

        if not user:
            user = User(
                phone_number=phone_number,
                role=UserRole.user,
            )
            user.set_password(generate_six_digits_code())
            db.session.add(user)
            db.session.commit()

        code_for_sms = generate_six_digits_code()
        send_sms_with_code = send_sms.delay(SmsEventsForUser.send_auth_sms, user, generated_code=code_for_sms)

        if send_sms_with_code:
            session['sms_code'] = code_for_sms
            session['sms_send'] = True
            session['user_phone'] = phone_number

            flash('СМС с кодом отправлено')
            return sms_confirmation()
        else:
            flash(Markup(f'''При отправке смс произошла ошибка, попробуйте еще раз или <a href="{url_for('user.login')}" 
            class="alert-link">авторизуйтесь по email</a>'''))
            return redirect(url_for('user.sms_auth'))

    else:
        for field, errors in form_phone_number.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {getattr(form_phone_number, field).label.text}: {error}')
    return redirect(url_for('user.sms_auth'))


@blueprint.route('/sms_confirmation')
def sms_confirmation():
    title = "Регистрация и авторизация по коду из смс"

    return render_template('user/sms_confirmation.html', page_title=title)


@blueprint.route('/check_sms', methods=['POST'])
def check_sms():
    is_sms_sent = session.get('sms_send', False)
    is_user_answer_right = False
    generated_sms_code = session['sms_code']
    user_phone = session['user_phone']
    user_code = request.form['user_code']

    if user_code == generated_sms_code:
        is_user_answer_right = True
        user = User.query.filter(User.phone_number == user_phone).first()
        login_user(user)
        save_products_into_db_from_session_cart(user)
        flash("Вы успешно вошли на сайт")

    return jsonify({"is_sms_sent": is_sms_sent, "is_user_answer_right": is_user_answer_right})
