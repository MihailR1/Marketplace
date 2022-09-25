from flask import  Blueprint, flash, render_template, redirect, url_for
from flask_login import current_user, login_user, logout_user

from webapp.model import db
from webapp.model import User
from webapp.user.forms import LoginForm, RegistrationForm

blueprint = Blueprint('user', __name__, url_prefix='/user')

@blueprint.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace.index'))
    title = "Авторизация"
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
        
        flash("Не правильный адрес или пароль")
        return redirect(url_for('user.login'))


@blueprint.route('/logout')
def logout():
    logout_user()
    flash('Вы успешно вышли из сайта')
    return redirect(url_for('marketplace.index'))


@blueprint.route('/register')
def register():
    if current_user.is_authenticated:
        return redirect(url_for('marketplace.index')) # До делать когда будет готова главная страница
    title = 'Регистрация'
    form = RegistrationForm()
    return render_template('user/registration.html', page_title=title, form=form)


@blueprint.route('/process-reg', methods=['POST'])
def process_reg():
    form = RegistrationForm()
    if form.validate_on_submit():

        new_user = User(
            email=form.email.data, 
            phone_number = form.phone_number.data, 
            full_name=form.full_name.data, 
            shipping_adress=form.shipping_adress.data, 
            role='user'
            )

        new_user.set_password(form.password.data)
        db.session.add(new_user)
        db.session.commit()
        flash('Вы успешно зарегистрировались')
    else:
        for field, errors in form.errors.items():
            for error in errors:
                name_field_error = getattr(form, field).label.text
                flash(f"Ошибка в поле {name_field_error}:{error}")
    return redirect(url_for('user.register'))