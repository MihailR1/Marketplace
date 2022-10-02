from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired, NumberRange

from webapp.model import Category

class AddNewProductForm(FlaskForm):

    def get_category_choices():
        return [(category.id, category.name) for category in Category.query.all()]

    category = SelectField('Категория товара', coerce=int, choices=get_category_choices, validators=[DataRequired()], default='выберите категорию', render_kw={"class": "form-control"})
    name = StringField('Название продукта', validators=[DataRequired()], render_kw={"class": "form-control"})
    price = IntegerField('Цена', validators=[DataRequired(), NumberRange(min=1, max=1000000)], render_kw={"class": "form-control"})
    description = TextAreaField('Описание', render_kw={"class": "form-control"})
    brand_name = StringField('Бренд', render_kw={"class": "form-control"})
    color = StringField('Цвет', render_kw={"class": "form-control"})
    gender = SelectField('Пол', choices=['мужской', 'женский', 'унисекс'], render_kw={"class": "form-control"})
    size = StringField('Размер', render_kw={"class": "form-control"})
    submit = SubmitField('Отправить!', render_kw={"class": "btn btn-primary"})


    