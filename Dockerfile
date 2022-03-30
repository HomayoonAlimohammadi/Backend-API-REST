FROM python:3.8
LABEL maintainer='HomayoonAlimohammadi'

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
COPY ./app /app

WORKDIR /app
EXPOSE 8000

RUN pip install -r requirements.txt && \
    adduser --disabled-password --no-create-home user

USER user


