FROM python:3.12.2-slim-bullseye

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME /app
WORKDIR $APP_HOME
ENV FLASK_APP run.py
ENV DEBUG True
COPY . ./

COPY requirements.txt .

# install python dependencies
#RUN pip3 install --upgrade pip
RUN python -3.12 -m  install --no-cache-dir -r requirements.txt

COPY env.sample .env

COPY . .

RUN python -3.12 -m flask db init
RUN python -3.12 -m flask db migrate
RUN python -3.12 -m flask db upgrade

# gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
