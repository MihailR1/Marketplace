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
UPLOAD_PATH = os.path.join(basedir, 'static', 'media')
ALLOWED_IMAGE = set(['png', 'jpg', 'jpeg'])
LOG_FILES_PATH = os.path.join(basedir, '..', 'logs', 'working_log.log')
UNISENDER_API_KEY = os.environ['UNISENDER_API_KEY']
SEND_EMAIL_URL = 'https://api.unisender.com/ru/api/sendEmail'
EMAIL_SENDER_NAME = 'Интернет Магазин SuperSite'
SENDER_EMAIL = 'no-reply@super1site.ru'
YOOMONEY_TOKEN = os.environ['YOOMONEY_TOKEN']
YOOMONEY_WALLET = os.environ['YOOMONEY_WALLET']
YOOMONEY_SECRET_KEY = os.environ['YOOMONEY_SECRET_KEY']
MAINSMS_PROJECT_NAME = os.environ['MAINSMS_PROJECT_NAME']
MAINSMS_API_KEY = os.environ['MAINSMS_API_KEY']
CELERY_BROKER_URL = "redis://localhost:6379"
CELERY_RESULT_BACKEND = "redis://localhost:6379"
