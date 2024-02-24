FROM python:3.12.2-slim-bullseye

# set environment variables
#ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

ENV APP_HOME /app
WORKDIR $APP_HOME
ENV ASSETS_ROOT=/static/assets
# install python dependencies
#RUN pip3 install --upgrade pip


COPY . ./
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 5000

# gunicorn
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 --timeout 0 run:app
