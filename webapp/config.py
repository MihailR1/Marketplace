import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ['DATABASE_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ['SECRET_KEY']
CACHE_TYPE = "SimpleCache"
CACHE_DEFAULT_TIMEOUT = 18000
JSON_AS_ASCII = False
UPLOAD_PATH = os.path.join(basedir, 'media')
ALLOWED_IMAGE = set(['png', 'jpg', 'jpeg'])
UNISENDER_KEY = os.environ['UNISENDER_API_KEY']
SEND_EMAIL_URL = 'https://api.unisender.com/ru/api/sendEmail'
EMAIL_SENDER_NAME = 'Интернет Магазин SuperSite'
SENDER_EMAIL = 'no-reply@super1site.ru'
