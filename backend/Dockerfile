FROM python:3.12

RUN mkdir /app
WORKDIR /app

RUN apt-get update && apt-get install -y libpq-dev gcc && apt-get clean

COPY requirements.txt /app
RUN pip install -U pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

COPY . /app

RUN adduser --disabled-password user
USER user