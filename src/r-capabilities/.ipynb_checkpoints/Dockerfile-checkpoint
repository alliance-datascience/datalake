FROM python:3.10-slim-buster

WORKDIR /app

COPY *.py .

COPY requirements.txt .

RUN pip install -U pip && pip install -r requirements.txt

COPY conf ./conf

COPY model ./model

COPY utils ./utils
