from flask_wtf import FlaskForm
from wtforms import BooleanField, StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError

from webapp.user.models import User


class LoginForm(FlaskForm):
    email = StringField('Электронный адрес', validators=[DataRequired()], render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"class": "form-control"})
    remember_me = BooleanField('Запомнить меня', default=True, render_kw={"class": "from-check-input"})
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-primary"})


class RegistrationForm(FlaskForm):
    email = StringField('Электронный адрес', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    phone_number = StringField('Номер телефона', render_kw={"class": "mask-phone form-control"})
    full_name = StringField('Полное имя', render_kw={"class": "form-control"})
    shipping_adress = StringField('Адрес доставки', render_kw={"class": "form-control"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={"class": "form-control"})
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')],
                              render_kw={"class": "form-control"})
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-primary"})

    def validate_email(self, email):
        user_count = User.query.filter_by(email=email.data).count()
        if user_count > 0:
            raise ValidationError('Пользователь с таким адресом уже существует')

    def validate_phone_number(self, phone_number):
        if phone_number.data:
            user_count = User.query.filter_by(phone_number=phone_number.data).count()
            if user_count > 0:
                raise ValidationError('Пользователь с таким номером телефона уже существует')


class SmsAuthForm(FlaskForm):
    phone_number = StringField('Номер телефона', validators=[DataRequired()], render_kw={"class": "mask-phone form-control"})
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-primary"})
