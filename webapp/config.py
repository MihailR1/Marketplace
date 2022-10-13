import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = os.environ['POSTGRES_URL']
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ['SECRET_KEY']
CACHE_TYPE = "SimpleCache"
CACHE_DEFAULT_TIMEOUT = 18000
JSON_AS_ASCII = False

UPLOAD_PATH = os.path.join(basedir, 'media')
ALLOWED_IMAGE = set(['png', 'jpg', 'jpeg'])
