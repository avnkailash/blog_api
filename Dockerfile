FROM python:3.6-alpine
MAINTAINER Kailash

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk add --update --no-cache jpeg-dev
RUN apk add --update --no-cache --virtual .tmp-build-deps \
    gcc libc-dev linux-headers musl-dev zlib zlib-dev
RUN pip install -r /requirements.txt
RUN apk del .tmp-build-deps

RUN mkdir /api
WORKDIR /api
COPY ./api /api

RUN mkdir -p /vol/web/media
RUN mkdir -p /vol/web/static
RUN adduser -D user
RUN chown -R user:user /vol/
RUN chmod -R 755 /vol/web
USER user