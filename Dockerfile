FROM python:3.12.1

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV FLASK_APP run.py
ENV DEBUG True
ENV APP_HOME /app
WORKDIR $APP_HOME
COPY . ./

COPY requirements.txt .

# install python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY env.sample .env

COPY . .

RUN flask db init
RUN flask db migrate
RUN flask db upgrade

# gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 main:app
