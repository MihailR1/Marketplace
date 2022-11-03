from webapp import create_app
from webapp.celery_app import celery

app = create_app()
app.app_context().push()
