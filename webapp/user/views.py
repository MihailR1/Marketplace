from turtle import title
from flask import Blueprint, flash, render_template, redirect, url_for, request
from flask_login import login_user, logout_user, login_required, current_user


from webapp.db import db
from webapp.user.forms import LoginForm, RegistrationForm, UpdateDataProfileUserForm
from webapp.user.models import User
from webapp.user.enums import EmailEventsForUser
from webapp.services.service_send_email import send_email
from webapp.services.service_count import count_favorite_products_current_user

blueprint = Blueprint('user', __name__, url_prefix='/users')


@blueprint.route('/login_register')
def login_or_register_user():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace.index'))

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
        count_favorite_products_current_user=count_favorite_products_current_user
    )


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
            role='user'
        )
        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались')
        send_email(EmailEventsForUser.hello_letter, new_user)
        return redirect(url_for('user.login_or_register_user'))

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
        count_favorite_products_current_user=count_favorite_products_current_user
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
        count_favorite_products_current_user=count_favorite_products_current_user
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
        flash("Чтобы изменить свои данные, необходимо авторизоваиться или зарегистрироваться")
        return redirect(request.referrer)