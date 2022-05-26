FROM python:3.9-alpine

ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt /requirements.txt
RUN apk update
RUN apk add make automake gcc g++ subversion python3-dev
RUN pip install -r /requirements.txt

# Install postgres client
RUN apk add --update --no-cache postgresql-client

# Install individual dependencies
# so that we could avoid install extra packages
RUN apk add --update --no-cache --virtual .tmp-build-deps \
	gcc libc-dev linux-headers postgresql-dev


# Remove dependencies
RUN mkdir /usersUI
WORKDIR .
COPY ./usersUI /usersUI

# [Security] Limit the scope of user who run the docker image
RUN adduser -D user

USER user