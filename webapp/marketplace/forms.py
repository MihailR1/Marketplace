from flask_wtf import FlaskForm
from wtforms import IntegerField, StringField, SubmitField, TextAreaField, SelectField, MultipleFileField
from wtforms.validators import DataRequired, NumberRange

from webapp.marketplace.models import Category
from webapp.marketplace.enum_marketplace import ProductSortingTypes


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
    submit = SubmitField('Отправить!', render_kw={"class": "cart-btn"})

    def __init__(self, *args, **kwargs):
        super(AddNewProductForm, self).__init__(*args, **kwargs)
        self.category.choices = [(category.id, category.name) for category in Category.query.all()]


class SearchForm(FlaskForm):
    search_input = StringField('Найти товар', validators=[DataRequired()],
                               render_kw={"class": "search-input", "placeholder": "Найти товар",
                                          "autocomplete": "off"})
    submit = SubmitField('Поиск', render_kw={"class": "button-search"})


class SortingProductForm(FlaskForm):
    type_sorting = SelectField('Сортировка', choices=[])
    submit = SubmitField('Выполнить', render_kw={"class": "cart-btn cart-btn-sort"})

    def __init__(self, *args, **kwargs):
        super(SortingProductForm, self).__init__(*args, **kwargs)
        self.type_sorting.choices = [[type_sorting.value, type_sorting.readable_values()] for type_sorting in ProductSortingTypes]
