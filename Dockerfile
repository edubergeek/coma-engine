# base image
FROM python:3.12.11-alpine

RUN apk add build-base
RUN apk add mariadb-dev mariadb-common mariadb-client mariadb-connector-c

RUN /usr/local/bin/python -m pip install --upgrade pip

# set working directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# add requirements (to leverage Docker cache)
ADD ./requirements.txt /usr/src/app/requirements.txt

# install requirements
RUN pip install -r requirements.txt

# copy project
COPY . /usr/src/app
