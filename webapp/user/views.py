from flask import Blueprint, flash, render_template, redirect, url_for, session, request
from flask_login import current_user, login_user, logout_user

from webapp.db import db
from webapp.user.forms import LoginForm, RegistrationForm
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser, UserRole
from webapp.services.service_send_email import send_email
from webapp.services.service_redirect_utils import get_redirect_target
from webapp.services.service_cart import save_products_into_db_from_session_cart

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
            return redirect(get_redirect_target())

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
            role=UserRole.user
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
