FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt /app

RUN pip install -r requirements.txt
RUN apt-get update && apt-get install -y procps

COPY . /app
