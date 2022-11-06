from celery import Celery

from webapp.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND

celery = Celery(__name__, backend=CELERY_RESULT_BACKEND, broker=CELERY_BROKER_URL)
