
FROM python:3
ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=webapp
ENV FLASK_RUN_HOST=0.0.0.0
WORKDIR /usr/src/app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
EXPOSE 8080
COPY . .
CMD ["flask", "run"]