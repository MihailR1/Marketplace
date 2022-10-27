from flask import Blueprint, flash, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user

from webapp.db import db
from webapp.user.forms import LoginForm, RegistrationForm, SmsAuthForm
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser
from webapp.services.service_send_email import send_email

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
    form = SmsAuthForm()

    if form.validate_on_submit():
        print(form.phone_number.data)
        get_user_from_db = User.query.filter(User.phone_number == form.phone_number.data).first()

        if not get_user_from_db:
            new_user = User(
                email=form.phone_number.data,
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
