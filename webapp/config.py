import os

basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'webapp.db')
SECRET_KEY = '*(!bkjAlkjklf-1(*u21oka(*!klWJKBQlksnih2'
SQLALCHEMY_TRACK_MODIFICATIONS = False
