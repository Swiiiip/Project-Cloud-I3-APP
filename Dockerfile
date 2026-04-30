FROM python:3.12-slim

WORKDIR /app

COPY src src
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
