from flask import Blueprint, flash, render_template, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user

from webapp.db import db
from webapp.user.forms import LoginForm, RegistrationForm, SmsAuthForm
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser, SmsEventsForUser
from webapp.services.service_send_email import send_email
from webapp.services.service_send_sms import delete_symbols_from_phone_number, generate_six_digits_code, send_sms

blueprint = Blueprint('user', __name__, url_prefix='/users')


@blueprint.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace.index'))
    title = "Войти"
    login_form = LoginForm()
    return render_template('user/login.html', page_title=title, form=login_form)


@blueprint.route('/process-login', methods=['POST'])
def process_login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash("Вы успешно вошли на сайт")
            return redirect(url_for('marketplace.index'))

        flash('Не правильные имя или пароль')
        return redirect(url_for('user.login'))


@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно разлогинились')
    return redirect(url_for('marketplace.index'))


@blueprint.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace.index'))
    title = "Регистрация"
    form = RegistrationForm()
    return render_template('user/registration.html', page_title=title, form=form)


@blueprint.route('/process-reg', methods=['POST'])
def process_reg():
    form = RegistrationForm()
    if form.validate_on_submit():
        new_user = User(
            email=form.email.data,
            role='user'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались')
        send_email(EmailEventsForUser.hello_letter, new_user)
        return redirect(url_for('user.login'))
    else:
        for field, errors in form.errors.items():
            for error in errors:
                flash("Ошибка в поле {}: {}".format(
                    getattr(form, field).label.text,
                    error
                ))
    return redirect(url_for('user.register'))


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
    status_sms = False
    if form_phone_number.validate_on_submit():
        phone_number = delete_symbols_from_phone_number(form_phone_number.phone_number.data)
        user = User.query.filter(User.phone_number == phone_number).first()

        if not user:
            new_user = User(
                phone_number=phone_number,
                role='user',
            )
            new_user.set_password(generate_six_digits_code())
            db.session.add(new_user)
        db.session.commit()
        code_for_sms = generate_six_digits_code()
        status_sms = send_sms(SmsEventsForUser.send_auth_sms, user, generated_code=code_for_sms)

        flash('СМС с кодом отправлено')
        redirect(url_for('user.sms_confirmation'))

    else:
        for field, errors in form_phone_number.errors.items():
            for error in errors:
                flash(f'Ошибка в поле {getattr(form_phone_number, field).label.text}: {error}')
        return redirect(url_for('user.sms_auth'))


@blueprint.route('/check_sms', methods=['POST'])
def check_sms(code):
    status_sms = False
    return jsonify({"is_sms_sent": status_sms})
