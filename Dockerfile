# syntax=docker/dockerfile:1
FROM python:3.10-alpine
WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
COPY ./app /code/app
# COPY ./resources /code/resources
RUN apk add --no-cache gcc musl-dev linux-headers ffmpeg postgresql-dev python3-dev 
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
RUN sleep 30s
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]