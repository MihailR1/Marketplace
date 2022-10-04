import os

from dotenv import load_dotenv

load_dotenv()
basedir = os.path.abspath(os.path.dirname(__file__))

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, '..', 'webapp.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = os.environ['SECRET_KEY']

UPLOAD_FOLDER = 'webapp/marketplace/files/img_product/'

ALLOWED_IMAGE = set(['png', 'jpg', 'jpeg'])