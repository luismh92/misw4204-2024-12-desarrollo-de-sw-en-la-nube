# syntax=docker/dockerfile:1
FROM python:3.9-alpine
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
# COPY ./resources /code/resources
RUN apk add --no-cache gcc musl-dev linux-headers ffmpeg postgresql-dev python3-dev 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 80