FROM python:3.13-alpine3.21 AS backend-build

RUN mkdir /app
WORKDIR /app

COPY requirements.txt /app
RUN pip install -U pip --no-cache-dir && pip install -r requirements.txt --no-cache-dir

FROM python:3.13-alpine3.21 AS backend-mid

RUN mkdir /app
WORKDIR /app

COPY --from=backend-build /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=backend-build /usr/local/bin/gunicorn /usr/local/bin

FROM backend-mid AS backend-prod

COPY . /app
RUN rm -r static nginx

RUN adduser --disabled-password user
USER user

FROM backend-mid AS backend-dev

COPY requirements_dev.txt /app

RUN pip install -U pip --no-cache-dir && pip install -r requirements_dev.txt --no-cache-dir

COPY . /app
RUN rm -r static nginx
