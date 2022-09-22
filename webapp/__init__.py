from flask import Flask, render_template
from flask_migrate import Migrate

from webapp.model import db


def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    db.init_app(app)  # Инициализация БД
    migrate = Migrate(app, db)  # Для миграции-изменения структуры БД

    @app.route('/')
    def index():
        title = 'Интернет Магазин'
        return render_template('index.html', page_title=title)

    return app
