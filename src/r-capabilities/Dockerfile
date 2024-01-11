FROM python:3.10-slim-buster


WORKDIR /app

COPY __init__.py .

COPY main.py .

COPY requirements.txt .

RUN pip install -U pip && pip install -r requirements.txt

COPY conf/ ./conf/

COPY model/ ./model/

COPY utils/ ./utils/

COPY serverStart.sh .

EXPOSE 8081

RUN chmod +x serverStart.sh

ENTRYPOINT ["./serverStart.sh"]