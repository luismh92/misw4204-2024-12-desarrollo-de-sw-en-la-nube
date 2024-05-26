# syntax=docker/dockerfile:1
FROM python:3.10-alpine
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
WORKDIR /code
# COPY ./resources /code/resources
RUN apk add --no-cache gcc musl-dev linux-headers ffmpeg postgresql-dev python3-dev nfs-utils g++
RUN pip install -r /code/requirements.txt
COPY . .
CMD uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 80