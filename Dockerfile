# syntax=docker/dockerfile:1
FROM python:3.10-ubuntu
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
# COPY ./resources /code/resources
RUN apt-get --no-cache gcc musl-dev linux-headers ffmpeg postgresql-dev python3-dev nfs-utils
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
CMD uvicorn app.main:app --reload --workers 1 --host 0.0.0.0 --port 80