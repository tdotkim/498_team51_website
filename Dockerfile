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
RUN pip install --no-cache-dir -r requirements.txt

COPY env.sample .env

COPY . .
COPY . ./

ENV FLASK_APP run.py
ENV DEBUG True
RUN flask db init
RUN flask db migrate
RUN flask db upgrade

# gunicorn
CMD exec gunicorn --bind 0.0.0.0:$PORT --workers 1 --threads 8 --timeout 0 run:app
