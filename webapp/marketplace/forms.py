from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, NumberRange, Email

from webapp.marketplace.models import Category


class AddNewProductForm(FlaskForm):
    category = SelectField('Категория товара', coerce=int, choices=[], validators=[DataRequired()],
                           default='выберите категорию', render_kw={"class": "form-control"})
    name = StringField('Название продукта', validators=[DataRequired()], render_kw={"class": "form-control"})
    price = IntegerField('Цена', validators=[DataRequired(), NumberRange(min=1, max=1000000)],
                         render_kw={"class": "form-control"})
    description = TextAreaField('Описание', render_kw={"class": "form-control"})
    brand_name = StringField('Бренд', render_kw={"class": "form-control"})
    color = StringField('Цвет', render_kw={"class": "form-control"})
    gender = SelectField('Пол', choices=['мужской', 'женский', 'унисекс'], render_kw={"class": "form-control"})
    size = StringField('Размер', render_kw={"class": "form-control"})
    photos = MultipleFileField('Добавить фото', validators=[DataRequired()])
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-primary"})

    def __init__(self, *args, **kwargs):
        super(AddNewProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]


class SearchForm(FlaskForm):
    search_input = StringField('Найти товар', validators=[DataRequired()],
                               render_kw={"class": "form-control mr-sm-2", "placeholder": "Найти товар",
                                          "autocomplete": "off"})
    submit = SubmitField('Поиск', render_kw={"class": "btn btn-outline-success my-2 my-sm-0"})


class CheckoutForm(FlaskForm):
    email = StringField('Электронный адрес', validators=[DataRequired(), Email()], render_kw={"class": "form-control"})
    phone_number = StringField('Номер телефона', render_kw={"class": "form-control"})
    full_name = StringField('Полное имя', validators=[DataRequired()], render_kw={"class": "form-control"})
    shipping_adress = StringField('Адрес доставки', validators=[DataRequired()], render_kw={"class": "form-control"})
    submit = SubmitField('Перейти к оплате', render_kw={"class": "btn btn-primary"})
